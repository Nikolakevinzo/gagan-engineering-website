import React, { act } from "react";
import { createRoot } from "react-dom/client";
import { MemoryRouter, Route, Routes, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { BLOG_ARTICLES } from "@/lib/blogData";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";
import Blog from "./Blog";
import BlogPost from "./BlogPost";
import ProductDetail from "./ProductDetail";
import Products from "./Products";
import Home from "./Home";
import AdminBlogForm from "./Admin/BlogForm";
import AdminProductForm from "./Admin/ProductForm";

jest.mock("@/lib/api", () => ({ api: { get: jest.fn(), post: jest.fn() } }));
jest.mock("sonner", () => ({ toast: { success: jest.fn(), error: jest.fn(), warning: jest.fn() } }));
jest.mock("@/components/AdminLayout", () => ({ useAdminAuth: () => ({ getAuthHeader: () => ({}) }) }));
jest.mock("@/components/ProductGallery", () => () => null);
// CRA's Jest 27 resolver predates the package exports used by React Router 7.
jest.mock("react-router-dom", () => {
  const { TextEncoder, TextDecoder } = require("util");
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
  return jest.requireActual("react-router/dist/development/index.js");
}, { virtual: true });

const article = {
  ...BLOG_ARTICLES[0],
  title: "Server Article",
  content: [{ type: "section", id: "intro", heading: "Introduction", text: "Server article content." }],
};
const product = { ...CATALOGUE_PRODUCTS[0], name: "Server Machine" };
const response = (data, status = 200) => ({ ok: status >= 200 && status < 300, status, json: async () => data });
const deferred = () => {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
};

let root;
let container;
let navigate;

function Navigation() {
  navigate = useNavigate();
  return null;
}

async function mount(Component, path, pattern = path) {
  await act(async () => {
    root.render(
      <MemoryRouter initialEntries={[path]}>
        <Navigation />
        <Routes>
          <Route path={pattern} element={<Component />} />
          <Route path="/admin/blogs" element={<div>Saved articles list</div>} />
          <Route path="/admin/products" element={<div>Saved products list</div>} />
        </Routes>
      </MemoryRouter>
    );
  });
}

async function fill(input, value) {
  await act(async () => {
    const prototype = input.tagName === "TEXTAREA" ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    Object.getOwnPropertyDescriptor(prototype, "value").set.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
}

async function submit() {
  await act(async () => container.querySelector("form").dispatchEvent(new Event("submit", { bubbles: true, cancelable: true })));
}

beforeEach(() => {
  global.IS_REACT_ACT_ENVIRONMENT = true;
  jest.clearAllMocks();
  localStorage.clear();
  global.fetch = jest.fn();
  window.scrollTo = jest.fn();
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);
});

afterEach(async () => {
  await act(async () => root.unmount());
  container.remove();
  jest.restoreAllMocks();
});

test.each([
  ["product", ProductDetail, `/products/${product.id}`, "/products/:id"],
  ["article", BlogPost, `/blog/${article.slug}`, "/blog/:slug"],
])("%s quotation failure keeps the enquiry for retry and only confirms accepted requests", async (_, Component, path, pattern) => {
  api.get.mockResolvedValue({ data: { product, related: [] } });
  fetch.mockResolvedValue(response({ article }));
  api.post.mockRejectedValueOnce(new Error("Connection unavailable"));
  jest.spyOn(console, "error").mockImplementation(() => {});
  await mount(Component, path, pattern);
  const inputs = container.querySelectorAll("form input");
  for (const [index, value] of ["Buyer Name", "buyer@example.test", "+910000000000", "India"].entries()) {
    if (inputs[index]) await fill(inputs[index], value);
  }
  await submit();
  expect(container.querySelector('[role="alert"]').textContent).toContain("not submitted");
  expect(container.querySelector("form input").value).toBe("Buyer Name");
  expect(container.querySelector('form button[type="submit"]').disabled).toBe(false);
  expect(toast.success).not.toHaveBeenCalled();
  expect(localStorage.getItem("gagan_cached_leads")).toBeNull();

  api.post.mockResolvedValueOnce({ data: {} });
  await submit();
  expect(toast.success).not.toHaveBeenCalled();
  expect(container.querySelector("form input").value).toBe("Buyer Name");

  api.post.mockResolvedValueOnce({ data: { lead_id: "accepted-fixture" } });
  await submit();
  expect(toast.success).toHaveBeenCalledTimes(1);
  expect(container.querySelector("form")).toBeNull();
});

test.each([
  ["product", ProductDetail, `/products/${product.id}`, "/products/:id", "/products/second-machine"],
  ["article", BlogPost, `/blog/${article.slug}`, "/blog/:slug", "/blog/second-article"],
])("a late %s quotation response never confirms an enquiry on a different page", async (_, Component, path, pattern, nextPath) => {
  api.get.mockResolvedValue({ data: { product, related: [] } });
  fetch.mockResolvedValue(response({ article }));
  await mount(Component, path, pattern);
  const inputs = container.querySelectorAll("form input");
  for (const [index, value] of ["Buyer Name", "buyer@example.test", "+910000000000", "India"].entries()) {
    if (inputs[index]) await fill(inputs[index], value);
  }
  const pending = deferred();
  api.post.mockReturnValueOnce(pending.promise);
  await submit();
  api.get.mockResolvedValueOnce({ data: { product: { ...product, id: "second-machine" }, related: [] } });
  fetch.mockResolvedValueOnce(response({ article: { ...article, slug: "second-article" } }));
  await act(async () => navigate(nextPath));
  await act(async () => pending.resolve({ data: { lead_id: "old-route-fixture" } }));
  expect(container.querySelector("form")).not.toBeNull();
  expect(container.querySelector('form button[type="submit"]').disabled).toBe(false);
  expect(toast.success).not.toHaveBeenCalled();
});

test("public blog listing honors an empty API list and ignores browser editor records", async () => {
  localStorage.setItem("gagan_custom_blogs", JSON.stringify([{ ...article, title: "Browser-only Article" }]));
  fetch.mockResolvedValue(response({ articles: [] }));
  await mount(Blog, "/blog");
  expect(container.textContent).toContain("No Engineering Guides Located");
  expect(container.querySelector('a[href^="/blog/"]')).toBeNull();
  expect(container.textContent).not.toContain("Browser-only Article");
});

test.each([[Products, "/products"], [Home, "/"]])("public catalogue honors an empty API list instead of seeds or editor records", async (Component, path) => {
  localStorage.setItem("gagan_custom_products", JSON.stringify([{ ...product, name: "Browser-only Machine" }]));
  api.get.mockResolvedValue({ data: { products: [] } });
  await mount(Component, path);
  expect(container.querySelector('a[href^="/products/10-tons"]')).toBeNull();
  expect(container.textContent).not.toContain("Browser-only Machine");
});

test("an unpublished article and an outage never resurrect a bundled seed", async () => {
  fetch.mockResolvedValueOnce(response({ article: { ...article, published: false } }));
  await mount(BlogPost, `/blog/${article.slug}`, "/blog/:slug");
  expect(container.textContent).toContain("Article Not Located");
  fetch.mockResolvedValueOnce(response({}, 503));
  await act(async () => navigate(`/blog/${BLOG_ARTICLES[1].slug}`));
  expect(container.textContent).toContain("Article Temporarily Unavailable");
  expect(container.textContent).not.toContain(BLOG_ARTICLES[1].title);
});

test("article route changes clear old metadata and ignore a late response", async () => {
  fetch.mockResolvedValueOnce(response({ article }));
  await mount(BlogPost, `/blog/${article.slug}`, "/blog/:slug");
  expect(document.title).toContain("Server Article");
  const slow = deferred();
  fetch.mockReturnValueOnce(slow.promise);
  await act(async () => navigate("/blog/slow-article"));
  expect(container.textContent).toContain("Loading Technical Guide");
  expect(document.title).not.toContain("Server Article");
  expect(document.querySelector('link[rel="canonical"]').href).toMatch(/\/blog\/slow-article$/);
  fetch.mockResolvedValueOnce(response({}, 404));
  await act(async () => navigate("/blog/missing-article"));
  await act(async () => slow.resolve(response({ article: { ...article, slug: "slow-article", title: "Late Article" } })));
  expect(container.textContent).toContain("Article Not Located");
  expect(container.textContent).not.toContain("Late Article");
  expect(document.querySelector('link[rel="canonical"]').href).toMatch(/\/blog\/missing-article$/);
  expect(document.querySelector('meta[name="robots"]').content).toContain("noindex");
});

test("missing product routes discard old product schema and ignore late responses", async () => {
  api.get.mockResolvedValueOnce({ data: { product, related: [] } });
  await mount(ProductDetail, `/products/${product.id}`, "/products/:id");
  const productSchema = JSON.parse(document.getElementById("jsonld-seo-schema").text).find((item) => item["@type"] === "Product");
  expect(productSchema.name).toBe("Server Machine");
  expect(productSchema.offers).toBeUndefined();
  expect(productSchema.review).toBeUndefined();
  expect(productSchema.aggregateRating).toBeUndefined();
  const slow = deferred();
  api.get.mockReturnValueOnce(slow.promise);
  await act(async () => navigate("/products/slow-machine"));
  api.get.mockRejectedValueOnce({ response: { status: 404 } });
  await act(async () => navigate("/products/missing-machine"));
  await act(async () => slow.resolve({ data: { product: { ...product, id: "slow-machine" } } }));
  expect(container.textContent).toContain("Machine Not Found");
  expect(document.querySelector('link[rel="canonical"]').href).toMatch(/\/products\/missing-machine$/);
  expect(document.querySelector('meta[name="robots"]').content).toContain("noindex");
  const missingPageSchema = JSON.parse(document.getElementById("jsonld-seo-schema").text);
  expect([].concat(missingPageSchema).some((item) => item["@type"] === "Product")).toBe(false);
});

test("failed admin article publication leaves edits in the editor without a fake local publication", async () => {
  fetch.mockResolvedValue(response({ detail: "Storage unavailable. Nothing was saved." }, 503));
  await mount(AdminBlogForm, "/admin/blogs/new");
  await fill(container.querySelector('input[placeholder^="e.g. Complete Guide"]'), "New Technical Guide");
  await fill(container.querySelector('textarea[placeholder^="Provide a compelling"]'), "Technical guide summary.");
  await submit();
  expect(container.querySelector('input[placeholder^="e.g. Complete Guide"]').value).toBe("New Technical Guide");
  expect(container.textContent).not.toContain("Saved articles list");
  expect(toast.success).not.toHaveBeenCalled();
  expect(toast.error).toHaveBeenCalled();
  expect(localStorage.getItem("gagan_custom_blogs")).toBeNull();
});

test("failed admin product save retains the form and reports failure without browser-only publication", async () => {
  fetch.mockResolvedValueOnce(response({ product }));
  await mount(AdminProductForm, `/admin/products/${product.id}/edit`, "/admin/products/:id/edit");
  fetch.mockResolvedValueOnce(response({ detail: "Storage unavailable. Nothing was saved." }, 503));
  await submit();
  expect(container.textContent).toContain("Nothing was saved");
  expect(container.querySelector("form")).not.toBeNull();
  expect(container.textContent).not.toContain("Product saved successfully");
  expect(localStorage.getItem("gagan_custom_products")).toBeNull();
});

test.each([
  ["article", AdminBlogForm, "/admin/blogs/new", "/admin/blogs/new"],
  ["product", AdminProductForm, `/admin/products/${product.id}/edit`, "/admin/products/:id/edit"],
])("a validation array from the %s save API reports a readable error and preserves the editor", async (kind, Component, path, pattern) => {
  if (kind === "product") fetch.mockResolvedValueOnce(response({ product }));
  await mount(Component, path, pattern);
  if (kind === "article") {
    await fill(container.querySelector('input[placeholder^="e.g. Complete Guide"]'), "New Technical Guide");
    await fill(container.querySelector('textarea[placeholder^="Provide a compelling"]'), "Technical guide summary.");
  }
  const titleInput = container.querySelector("form input");
  const titleBeforeSave = titleInput.value;
  fetch.mockResolvedValueOnce(response({ detail: [{ loc: ["body", "name"], msg: "Validation failed", type: "value_error" }] }, 422));
  await submit();
  expect(container.querySelector("form input").value).toBe(titleBeforeSave);
  expect(container.querySelector("form")).not.toBeNull();
  expect(toast.success).not.toHaveBeenCalled();
  if (kind === "article") expect(toast.error).toHaveBeenCalledWith(expect.stringContaining("Article was not saved"));
  else expect(container.textContent).toContain("Product was not saved");
});

test.each([
  ["unavailable storage", { detail: "Product storage is unavailable. Nothing was saved." }, "Nothing was saved", []],
  ["partial progress", { detail: { message: "Import stopped. Earlier products were saved; review these IDs before retrying.", error: "Storage unavailable", created_ids: ["saved-machine"], skipped_ids: ["duplicate-machine"] } }, "Import stopped", ["Confirmed saved IDs: saved-machine", "Skipped duplicate IDs: duplicate-machine"]],
  ["an unexpected error object", { detail: { error: { reason: "unavailable" } } }, "Import failed", []],
])("bulk import with %s retains JSON and reports failure without claiming completion", async (_, data, message, progress) => {
  await mount(AdminProductForm, "/admin/products/new");
  await act(async () => Array.from(container.querySelectorAll("button")).find((button) => button.textContent === "Bulk Import from JSON").click());
  const jsonInput = container.querySelector('textarea[rows="8"]');
  const payload = JSON.stringify([{ name: "Saved Machine", image: "/machine.png" }, { name: "Remaining Machine", image: "/machine.png" }]);
  await fill(jsonInput, payload);
  fetch.mockResolvedValueOnce(response(data, 503));
  await act(async () => Array.from(container.querySelectorAll("button")).find((button) => button.textContent === "Import Products").click());
  expect(jsonInput.value).toBe(payload);
  expect(container.textContent).toContain(message);
  expect(container.textContent).toContain("Review the product list before retrying");
  for (const text of progress) expect(container.textContent).toContain(text);
  expect(container.textContent).not.toContain("✓ Imported");
});

test("bulk import clears JSON only after a valid completion response", async () => {
  await mount(AdminProductForm, "/admin/products/new");
  await act(async () => Array.from(container.querySelectorAll("button")).find((button) => button.textContent === "Bulk Import from JSON").click());
  const jsonInput = container.querySelector('textarea[rows="8"]');
  const payload = JSON.stringify([{ name: "Machine", image: "/machine.png" }]);
  await fill(jsonInput, payload);
  fetch.mockResolvedValueOnce(response({ status: "completed", created: 1, skipped: 0 }));
  await act(async () => Array.from(container.querySelectorAll("button")).find((button) => button.textContent === "Import Products").click());
  expect(jsonInput.value).toBe(payload);
  expect(container.textContent).toContain("confirmation could not be verified");
  expect(container.textContent).not.toContain("✓ Imported");
  fetch.mockResolvedValueOnce(response({ status: "completed", created: 1, skipped: 0, created_ids: ["machine"], skipped_ids: [] }));
  await act(async () => Array.from(container.querySelectorAll("button")).find((button) => button.textContent === "Import Products").click());
  expect(jsonInput.value).toBe("");
  expect(container.textContent).toContain("✓ Imported 1 products.");
});
