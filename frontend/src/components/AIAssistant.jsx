import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Bot, X, Send, Sparkles, MessageCircle, Phone, ArrowRight, CheckCircle2 } from "lucide-react";
import { CATALOGUE_PRODUCTS } from "@/lib/catalogueData";
import { BUSINESS } from "@/lib/business";
import { api } from "@/lib/api";

const QUICK_QUESTIONS = [
  "Which bra cup machine for 500 pcs/day?",
  "What are the specs of 10-Ton Decoiler?",
  "Explain Automatic CTL Line capacity",
  "How to visit Khopoli manufacturing works?"
];

export default function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Namaste! I am the Gagan Engineering AI Machinery Advisor. How can I help you choose the right industrial machinery for your factory today?",
      suggestedProducts: []
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Local Intelligent Machine Matching Engine
  const generateLocalResponse = (query) => {
    const q = query.toLowerCase();

    // 1. Bra cup queries
    if (q.includes("bra") || q.includes("lingerie") || q.includes("cup") || q.includes("foam") || q.includes("moulding")) {
      const match = CATALOGUE_PRODUCTS.filter((p) => p.categorySlug === "bra-cup-moulding-machine");
      return {
        text: `For bra cup & lingerie production, we manufacture 4 specialized machines at our Khopoli facility:\n\n1. **Double Head Electric Bra Cup Moulding Machine** (~400–600 pcs/shift, twin-station PID control).\n2. **Bra Cup Fabric Moulding Machine** (for woven/laminated fabrics, 25–40s cycle).\n3. **Foam Bra Cup Moulding Machine** (for PU & memory foam).\n4. **Padded Bra Cup Moulding Machine** (multi-layer composite moulding).\n\nAll machines operate on 3-Phase 415V with interchangeable moulds from sizes 28A to 44DD.`,
        suggestedProducts: match
      };
    }

    // 2. Decoiler queries
    if (q.includes("decoiler") || q.includes("uncoiler") || q.includes("10 ton") || q.includes("coil")) {
      const match = CATALOGUE_PRODUCTS.filter((p) => p.id.includes("decoiler"));
      return {
        text: `Our **10 Tons Hydraulic Decoiler** is built for heavy-duty coil handling:\n\n• **Capacity**: 10,000 kg (10 Metric Tons)\n• **Mandrel Expansion**: Hydraulic (480–520 mm ID)\n• **Drive**: 7.5 HP Geared Motor with motorized forward/reverse\n• **Braking**: Pneumatic disc brake for controlled line tension\n• **Application**: Roll forming lines, CTL lines, and roofing sheet production.`,
        suggestedProducts: match
      };
    }

    // 3. Cut to Length queries
    if (q.includes("ctl") || q.includes("cut to length") || q.includes("leveler") || q.includes("shearing")) {
      const match = CATALOGUE_PRODUCTS.filter((p) => p.id === "automatic-ctl-machine");
      return {
        text: `Our **Automatic Cut To Length (CTL) Machine** is a complete high-speed processing line:\n\n• **Max Thickness**: Up to 6.0 mm steel\n• **Line Speed**: 20 Meters / Minute\n• **Leveler**: 9-Roll gear driven leveler with EN31 hardened steel rolls (50–52 HRC)\n• **Decoiler**: 10-Ton hydraulic with sensor control\n• **Control**: Optical encoder with Touch Screen VFD PLC (±0.5mm accuracy)\n• **Total Connected Load**: 18 HP`,
        suggestedProducts: match
      };
    }

    // 4. Purlin / Roofing / Crimping queries
    if (q.includes("purlin") || q.includes("roofing") || q.includes("crimping") || q.includes("corrugated") || q.includes("c/z")) {
      const match = CATALOGUE_PRODUCTS.filter((p) => p.categorySlug === "roll-forming-sheet-metal");
      return {
        text: `For Pre-Engineered Building (PEB) and roofing fabrication, we build:\n\n• **C / Z Purlin Roll Forming Machine**: Quick changeover between C & Z profiles (100–300mm), 1.5–3.0mm thickness, integrated hydraulic punch & cut.\n• **Automatic Roofing Sheet Crimping Machine**: High-speed curved arch forming for PPGI/GI sheets up to 1250mm width.\n• **Corrugated Sheets Making Machine**: Continuous sinusoidal roofing roll former.`,
        suggestedProducts: match
      };
    }

    // 5. Factory location / Visit / Contact / Warranty queries
    if (q.includes("location") || q.includes("address") || q.includes("visit") || q.includes("khopoli") || q.includes("contact") || q.includes("warranty") || q.includes("price")) {
      return {
        text: `**Gagan Engineering Works** has been operating since 2006.\n\n📍 **Works Address**: Mumbai-Pune Highway, near Star Garage, Navanath Colony, Yashwant Nagar, Khopoli, Maharashtra 410203.\n📞 **Direct Call**: ${BUSINESS.phoneDisplay}\n💬 **WhatsApp**: +${BUSINESS.phoneRaw}\n⭐ **IndiaMART Rating**: 4.0/5.0 with Pan-India dispatch & 1-Year Comprehensive Warranty.\n\nWould you like a formal price quotation sent to your WhatsApp or email?`,
        suggestedProducts: []
      };
    }

    // General fallback
    return {
      text: `Gagan Engineering Works specializes in heavy-duty **Bra Cup Moulding Presses**, **10-Ton Hydraulic Decoilers**, **C/Z Purlin Roll Formers**, **Automatic Cut-To-Length Lines**, and **Roofing Sheet Machinery**.\n\nPlease share your specific production capacity or raw material thickness, or tap WhatsApp below to discuss directly with our chief engineer.`,
      suggestedProducts: CATALOGUE_PRODUCTS.slice(0, 3)
    };
  };

  const handleSend = async (userText) => {
    const textToSend = userText || input;
    if (!textToSend.trim()) return;

    // Add user message
    const userMsg = { sender: "user", text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      // Try backend API first, if offline fallback to local AI engine
      const res = await api.post("/ai/ask", { question: textToSend }).catch(() => null);

      if (res && res.data && res.data.answer) {
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: res.data.answer,
            suggestedProducts: res.data.suggestedProducts || []
          }
        ]);
      } else {
        const local = generateLocalResponse(textToSend);
        setMessages((prev) => [
          ...prev,
          {
            sender: "ai",
            text: local.text,
            suggestedProducts: local.suggestedProducts
          }
        ]);
      }
    } catch {
      const local = generateLocalResponse(textToSend);
      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text: local.text,
          suggestedProducts: local.suggestedProducts
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        data-testid="ai-assistant-toggle"
        aria-label="Open Gagan AI Machinery Advisor"
        className="fixed bottom-24 right-6 z-40 bg-[#FF5722] hover:bg-[#F4511E] text-white p-3.5 rounded-full shadow-2xl flex items-center gap-2.5 border border-white/20 transition-all hover:scale-105 active:scale-95 group"
      >
        <Bot className="w-6 h-6 animate-pulse" />
        <span className="hidden sm:inline font-mono text-xs tracking-wider uppercase font-semibold pr-1">
          AI Machine Advisor
        </span>
      </button>

      {/* Interactive Modal Chat Window */}
      {isOpen && (
        <div
          data-testid="ai-assistant-modal"
          className="fixed bottom-6 right-6 z-50 w-[95vw] sm:w-[420px] max-h-[85vh] h-[600px] bg-[#0A0A0C] border border-[#27272A] rounded-lg shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-300"
        >
          {/* Header */}
          <div className="bg-[#121214] border-b border-[#27272A] p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded bg-[#FF5722]/10 border border-[#FF5722]/40 flex items-center justify-center text-[#FF5722]">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="font-display tracking-wider text-white text-lg flex items-center gap-2">
                  GAGAN AI ADVISOR
                  <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-ping" />
                </div>
                <div className="mono text-[10px] text-white/50 tracking-wider uppercase">
                  Industrial Machinery Consultant
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white/60 hover:text-white p-1 rounded"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 text-sm">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}
              >
                <div
                  className={`p-3.5 rounded-lg max-w-[88%] leading-relaxed ${
                    m.sender === "user"
                      ? "bg-[#FF5722] text-white rounded-br-none"
                      : "bg-[#16161A] text-white/90 border border-white/5 rounded-bl-none"
                  }`}
                >
                  <div className="whitespace-pre-line text-[13px]">{m.text}</div>

                  {/* Suggested Products Cards if any */}
                  {m.suggestedProducts && m.suggestedProducts.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                      <div className="mono text-[10px] tracking-wider uppercase text-[#FF5722] font-semibold">
                        Recommended Machines:
                      </div>
                      {m.suggestedProducts.map((p) => (
                        <Link
                          key={p.id}
                          to={`/products/${p.id}`}
                          onClick={() => setIsOpen(false)}
                          className="flex items-center gap-2.5 p-2 bg-black/40 hover:bg-black/80 border border-white/10 rounded transition-colors group"
                        >
                          <img
                            src={p.image}
                            alt={p.name}
                            className="w-10 h-10 object-cover rounded bg-zinc-900 shrink-0"
                          />
                          <div className="flex-1 min-w-0">
                            <div className="text-xs font-medium text-white truncate group-hover:text-[#FF5722]">
                              {p.name}
                            </div>
                            <div className="text-[10px] text-white/50 mono truncate">
                              {p.category}
                            </div>
                          </div>
                          <ArrowRight className="w-3.5 h-3.5 text-[#FF5722] shrink-0" />
                        </Link>
                      ))}
                    </div>
                  )}
                </div>

                {m.sender === "ai" && (
                  <div className="flex items-center gap-2 mt-2 ml-1">
                    <a
                      href={`https://wa.me/${BUSINESS.phoneRaw}?text=${encodeURIComponent("Hello Gagan Engineering, I was consulting with your AI Advisor and would like a quotation.")}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 mono text-[10px] bg-green-950/60 hover:bg-green-900/80 text-green-400 border border-green-700/50 px-2 py-1 rounded transition-colors"
                    >
                      <MessageCircle className="w-3 h-3" /> WhatsApp Quote
                    </a>
                    <a
                      href={`tel:${BUSINESS.phone}`}
                      className="inline-flex items-center gap-1 mono text-[10px] bg-zinc-800 hover:bg-zinc-700 text-white/80 border border-zinc-700 px-2 py-1 rounded transition-colors"
                    >
                      <Phone className="w-3 h-3" /> Call Works
                    </a>
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className="flex items-center gap-2 text-white/50 mono text-xs p-2">
                <Sparkles className="w-4 h-4 text-[#FF5722] animate-spin" />
                Analyzing machine specifications...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          <div className="p-2.5 bg-[#101012] border-t border-[#27272A] overflow-x-auto whitespace-nowrap flex gap-2">
            {QUICK_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(q)}
                className="mono text-[10px] text-white/70 hover:text-white bg-zinc-900 hover:bg-zinc-800 border border-zinc-700/80 px-2.5 py-1 rounded transition-colors shrink-0"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="p-3 bg-[#121214] border-t border-[#27272A] flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about machine specs, power, output..."
              className="flex-1 bg-black/60 border border-zinc-700 text-white text-xs px-3 py-2.5 rounded focus:outline-none focus:border-[#FF5722]"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className="bg-[#FF5722] hover:bg-[#F4511E] disabled:opacity-40 text-white p-2.5 rounded transition-colors"
              aria-label="Send"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
