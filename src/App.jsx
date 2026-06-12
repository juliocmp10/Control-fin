import { useState, useMemo, useCallback } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, LineChart, Line, PieChart, Pie, Cell, ReferenceLine
} from "recharts";

// ─── CONSTANTES ──────────────────────────────────────────────────────────────
const CORES = {
  bg: "#0F1117", card: "#1A1D2E", verde: "#00C896", ambar: "#F59E0B",
  vermelho: "#EF4444", textoPrimario: "#F1F5F9", textoSecundario: "#94A3B8",
  borda: "#2D3148", cardHover: "#222640",
};

const CATEGORIAS = {
  "MORADIA":               { cor: "#3B82F6", sub: ["Aluguel","Luz/Água/Gás","Internet/TV","Condomínio","Outros Moradia"], emoji: "🏠" },
  "ALIMENTAÇÃO":           { cor: "#F97316", sub: ["Mercado","Delivery/Restaurante","Padaria/Café","Outros Alimentação"], emoji: "🍽️" },
  "LAZER":                 { cor: "#06B6D4", sub: ["Saídas/Bares","Viagens","Equipamentos","Streaming/Entretenimento","Outros Lazer"], emoji: "🎉" },
  "CRIPTO & INVESTIMENTO": { cor: "#A855F7", sub: ["Bitcoin (BTC)","Solana (SOL)","HYPE","Outros Cripto","Poupança/CDB"], emoji: "📈" },
  "TRANSPORTE":            { cor: "#6B7280", sub: ["Gasolina","Estacionamento","Manutenção Carro/Outros","Uber/Táxi","Ônibus/Metrô"], emoji: "🚗" },
  "SAÚDE":                 { cor: "#10B981", sub: ["Remédios/Farmácia","Academia/Esporte","Plano de Saúde","Consultas"], emoji: "❤️" },
  "PESSOAL":               { cor: "#EC4899", sub: ["Roupas/Calçados","Eletrônicos","Assinaturas","Outros Pessoal"], emoji: "👤" },
  "META CARRO":            { cor: "#F59E0B", sub: ["Reserva"], emoji: "🚘" },
  "RENDA":                 { cor: "#00C896", sub: ["Salário","Renda Extra","Freelance","Investimento/Rendimento"], emoji: "💰" },
};

const MESES_NOMES = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
const MESES_COMPLETOS = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"];

const hoje = new Date();
const MES_ATUAL = hoje.getMonth() + 1;
const ANO_ATUAL = hoje.getFullYear();

// ─── DADOS DE EXEMPLO ────────────────────────────────────────────────────────
const gerarId = () => Math.random().toString(36).substr(2,9);

const DADOS_EXEMPLO = [
  // Janeiro
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-03`,descricao:"Energia elétrica",categoria:"MORADIA",subcategoria:"Luz/Água/Gás",valor:145,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-04`,descricao:"Internet",categoria:"MORADIA",subcategoria:"Internet/TV",valor:100,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-06`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:380,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-08`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:180,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-10`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-12`,descricao:"Aporte BTC",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Bitcoin (BTC)",valor:200,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-15`,descricao:"Bar com amigos",categoria:"LAZER",subcategoria:"Saídas/Bares",valor:120,tipo:"SAÍDA"},
  {id:gerarId(),mes:1,ano:ANO_ATUAL,data:`${ANO_ATUAL}-01-18`,descricao:"Farmácia",categoria:"SAÚDE",subcategoria:"Remédios/Farmácia",valor:60,tipo:"SAÍDA"},
  // Fevereiro
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-03`,descricao:"Energia",categoria:"MORADIA",subcategoria:"Luz/Água/Gás",valor:130,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-05`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:360,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-07`,descricao:"iFood",categoria:"ALIMENTAÇÃO",subcategoria:"Delivery/Restaurante",valor:90,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-10`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-12`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:160,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-14`,descricao:"Aporte SOL",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Solana (SOL)",valor:150,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-18`,descricao:"Netflix + Spotify",categoria:"LAZER",subcategoria:"Streaming/Entretenimento",valor:55,tipo:"SAÍDA"},
  {id:gerarId(),mes:2,ano:ANO_ATUAL,data:`${ANO_ATUAL}-02-20`,descricao:"Academia",categoria:"SAÚDE",subcategoria:"Academia/Esporte",valor:80,tipo:"SAÍDA"},
  // Março
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-01`,descricao:"Freela Fiverr",categoria:"RENDA",subcategoria:"Freelance",valor:250,tipo:"ENTRADA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-05`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:400,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-08`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:170,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-10`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-12`,descricao:"Aporte BTC",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Bitcoin (BTC)",valor:300,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-15`,descricao:"Saída balada",categoria:"LAZER",subcategoria:"Saídas/Bares",valor:200,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-18`,descricao:"Energia",categoria:"MORADIA",subcategoria:"Luz/Água/Gás",valor:155,tipo:"SAÍDA"},
  {id:gerarId(),mes:3,ano:ANO_ATUAL,data:`${ANO_ATUAL}-03-20`,descricao:"Roupas",categoria:"PESSOAL",subcategoria:"Roupas/Calçados",valor:180,tipo:"SAÍDA"},
  // Abril
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-04`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:390,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-06`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:190,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-08`,descricao:"Manutenção carro",categoria:"TRANSPORTE",subcategoria:"Manutenção Carro/Outros",valor:350,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-10`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-14`,descricao:"Aporte SOL",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Solana (SOL)",valor:200,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-18`,descricao:"Restaurante",categoria:"ALIMENTAÇÃO",subcategoria:"Delivery/Restaurante",valor:80,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-20`,descricao:"Internet",categoria:"MORADIA",subcategoria:"Internet/TV",valor:100,tipo:"SAÍDA"},
  {id:gerarId(),mes:4,ano:ANO_ATUAL,data:`${ANO_ATUAL}-04-22`,descricao:"Farmácia",categoria:"SAÚDE",subcategoria:"Remédios/Farmácia",valor:45,tipo:"SAÍDA"},
  // Maio
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-03`,descricao:"Energia",categoria:"MORADIA",subcategoria:"Luz/Água/Gás",valor:140,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-05`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:420,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-07`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:175,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-10`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-12`,descricao:"Freela foto",categoria:"RENDA",subcategoria:"Renda Extra",valor:150,tipo:"ENTRADA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-15`,descricao:"Bar amigos",categoria:"LAZER",subcategoria:"Saídas/Bares",valor:150,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-18`,descricao:"Aporte BTC",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Bitcoin (BTC)",valor:200,tipo:"SAÍDA"},
  {id:gerarId(),mes:5,ano:ANO_ATUAL,data:`${ANO_ATUAL}-05-22`,descricao:"Estacionamento",categoria:"TRANSPORTE",subcategoria:"Estacionamento",valor:40,tipo:"SAÍDA"},
  // Junho
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-01`,descricao:"Salário Exército",categoria:"RENDA",subcategoria:"Salário",valor:4800,tipo:"ENTRADA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-01`,descricao:"Freela Fiverr",categoria:"RENDA",subcategoria:"Freelance",valor:200,tipo:"ENTRADA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-02`,descricao:"Aluguel",categoria:"MORADIA",subcategoria:"Aluguel",valor:1200,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-02`,descricao:"Energia elétrica",categoria:"MORADIA",subcategoria:"Luz/Água/Gás",valor:140,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-03`,descricao:"Internet",categoria:"MORADIA",subcategoria:"Internet/TV",valor:100,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-04`,descricao:"Supermercado",categoria:"ALIMENTAÇÃO",subcategoria:"Mercado",valor:380,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-05`,descricao:"iFood jantar",categoria:"ALIMENTAÇÃO",subcategoria:"Delivery/Restaurante",valor:65,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-06`,descricao:"Gasolina",categoria:"TRANSPORTE",subcategoria:"Gasolina",valor:185,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-07`,descricao:"Aporte BTC",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Bitcoin (BTC)",valor:300,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-08`,descricao:"Farmácia",categoria:"SAÚDE",subcategoria:"Remédios/Farmácia",valor:55,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-10`,descricao:"Uber",categoria:"TRANSPORTE",subcategoria:"Uber/Táxi",valor:40,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-11`,descricao:"Saída bar",categoria:"LAZER",subcategoria:"Saídas/Bares",valor:130,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-15`,descricao:"Reserva Carro",categoria:"META CARRO",subcategoria:"Reserva",valor:500,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-16`,descricao:"Aporte SOL",categoria:"CRIPTO & INVESTIMENTO",subcategoria:"Solana (SOL)",valor:150,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-17`,descricao:"Academia",categoria:"SAÚDE",subcategoria:"Academia/Esporte",valor:80,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-18`,descricao:"Roupas",categoria:"PESSOAL",subcategoria:"Roupas/Calçados",valor:120,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-22`,descricao:"Estacionamento",categoria:"TRANSPORTE",subcategoria:"Estacionamento",valor:35,tipo:"SAÍDA"},
  {id:gerarId(),mes:6,ano:ANO_ATUAL,data:`${ANO_ATUAL}-06-28`,descricao:"Assinaturas",categoria:"PESSOAL",subcategoria:"Assinaturas",valor:55,tipo:"SAÍDA"},
];

// ─── HELPERS ─────────────────────────────────────────────────────────────────
const formatBRL = (v) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const formatData = (d) => {
  if (!d) return "";
  const [y, m, day] = d.split("-");
  return `${day} ${MESES_NOMES[parseInt(m) - 1]}`;
};

// ─── ESTILOS BASE ─────────────────────────────────────────────────────────────
const S = {
  app: { minHeight: "100vh", background: CORES.bg, color: CORES.textoPrimario, fontFamily: "'Inter', sans-serif", paddingBottom: 80 },
  card: { background: CORES.card, borderRadius: 16, padding: 20, border: `1px solid ${CORES.borda}`, boxShadow: "0 4px 24px rgba(0,0,0,0.4)" },
  input: { background: "#0F1117", border: `1px solid ${CORES.borda}`, borderRadius: 8, padding: "10px 14px", color: CORES.textoPrimario, fontSize: 14, width: "100%", outline: "none" },
  btn: (bg, color="#fff") => ({ background: bg, color, border: "none", borderRadius: 8, padding: "10px 18px", cursor: "pointer", fontWeight: 600, fontSize: 14, transition: "opacity .2s" }),
  label: { fontSize: 12, color: CORES.textoSecundario, marginBottom: 6, display: "block", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" },
  badge: (cor) => ({ background: cor + "22", color: cor, borderRadius: 6, padding: "3px 10px", fontSize: 12, fontWeight: 600, display: "inline-flex", alignItems: "center", gap: 4 }),
  nav: { position: "fixed", bottom: 0, left: 0, right: 0, background: CORES.card, borderTop: `1px solid ${CORES.borda}`, display: "flex", zIndex: 100 },
  navItem: (ativo) => ({ flex: 1, padding: "10px 4px", display: "flex", flexDirection: "column", alignItems: "center", gap: 3, cursor: "pointer", background: "none", border: "none", color: ativo ? CORES.verde : CORES.textoSecundario, fontSize: 10, fontWeight: ativo ? 700 : 400, transition: "color .2s" }),
  secao: { maxWidth: 800, margin: "0 auto", padding: "20px 16px" },
};

// ─── TOOLTIP CUSTOMIZADO ─────────────────────────────────────────────────────
const TooltipCustom = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: CORES.card, border: `1px solid ${CORES.borda}`, borderRadius: 10, padding: "10px 14px" }}>
      <p style={{ color: CORES.textoSecundario, fontSize: 12, marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color, fontSize: 13, fontWeight: 600 }}>{p.name}: {formatBRL(p.value)}</p>
      ))}
    </div>
  );
};

// ─── PAINEL ───────────────────────────────────────────────────────────────────
function Painel({ transacoes, mes, ano, setMes, setAno }) {
  const txMes = useMemo(() => transacoes.filter(t => t.mes === mes && t.ano === ano), [transacoes, mes, ano]);
  const entradas = useMemo(() => txMes.filter(t => t.tipo === "ENTRADA").reduce((s, t) => s + t.valor, 0), [txMes]);
  const saidas   = useMemo(() => txMes.filter(t => t.tipo === "SAÍDA").reduce((s, t) => s + t.valor, 0), [txMes]);
  const saldo    = entradas - saidas;
  const taxaPoupanca = entradas > 0 ? ((entradas - saidas) / entradas * 100) : 0;

  const porCategoria = useMemo(() => {
    const acc = {};
    txMes.filter(t => t.tipo === "SAÍDA" && t.categoria !== "META CARRO").forEach(t => {
      acc[t.categoria] = (acc[t.categoria] || 0) + t.valor;
    });
    return Object.entries(acc).sort((a, b) => b[1] - a[1]);
  }, [txMes]);

  const maxCat = porCategoria.length ? porCategoria[0][1] : 1;

  const top5 = useMemo(() =>
    [...txMes].filter(t => t.tipo === "SAÍDA").sort((a, b) => b.valor - a.valor).slice(0, 5),
    [txMes]
  );

  const lazerGasto = txMes.filter(t => t.categoria === "LAZER").reduce((s, t) => s + t.valor, 0);
  const reservaGasto = txMes.filter(t => t.categoria === "META CARRO").reduce((s, t) => s + t.valor, 0);

  return (
    <div style={S.secao}>
      {/* Seletor mês */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20, gap: 10 }}>
        <div style={{ display: "flex", overflowX: "auto", gap: 6, paddingBottom: 4, flex: 1 }}>
          {MESES_NOMES.map((m, i) => (
            <button key={i} onClick={() => setMes(i + 1)} style={{
              ...S.btn(mes === i + 1 ? CORES.verde : CORES.card),
              color: mes === i + 1 ? "#000" : CORES.textoSecundario,
              padding: "6px 12px", fontSize: 13, whiteSpace: "nowrap",
              border: `1px solid ${mes === i + 1 ? CORES.verde : CORES.borda}`
            }}>{m}</button>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <button onClick={() => setAno(a => a - 1)} style={{ ...S.btn(CORES.card), padding: "6px 10px", border: `1px solid ${CORES.borda}` }}>‹</button>
          <span style={{ fontWeight: 700, fontSize: 14 }}>{ano}</span>
          <button onClick={() => setAno(a => a + 1)} style={{ ...S.btn(CORES.card), padding: "6px 10px", border: `1px solid ${CORES.borda}` }}>›</button>
        </div>
      </div>

      {/* Alertas */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 20 }}>
        {entradas > 0 && lazerGasto > entradas * 0.2 && (
          <span style={{ ...S.badge(CORES.vermelho), padding: "6px 12px" }}>🔴 Lazer acima de 20% da renda</span>
        )}
        {reservaGasto === 0 && (
          <span style={{ ...S.badge(CORES.ambar), padding: "6px 12px" }}>🟡 Sem reserva pro carro este mês</span>
        )}
        <span style={{
          ...S.badge(taxaPoupanca >= 10 ? CORES.verde : taxaPoupanca >= 0 ? CORES.ambar : CORES.vermelho),
          padding: "6px 12px"
        }}>
          {taxaPoupanca >= 10 ? "🟢" : taxaPoupanca >= 0 ? "🟡" : "🔴"} Taxa de poupança: {taxaPoupanca.toFixed(1)}%
        </span>
      </div>

      {/* Cards resumo */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 24 }}>
        {[
          { label: "Entradas", valor: entradas, cor: CORES.verde },
          { label: "Saídas",   valor: saidas,   cor: CORES.vermelho },
          { label: "Saldo",    valor: saldo,    cor: saldo >= 0 ? CORES.verde : CORES.vermelho },
        ].map((c, i) => (
          <div key={i} style={{ ...S.card, textAlign: "center" }}>
            <p style={{ fontSize: 11, color: CORES.textoSecundario, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>{c.label}</p>
            <p style={{ fontSize: 18, fontWeight: 800, color: c.cor }}>{formatBRL(c.valor)}</p>
          </div>
        ))}
      </div>

      {/* Breakdown por categoria */}
      {porCategoria.length > 0 && (
        <div style={{ ...S.card, marginBottom: 20 }}>
          <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>📂 Gastos por Categoria</p>
          {porCategoria.map(([cat, val]) => (
            <div key={cat} style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <span style={S.badge(CATEGORIAS[cat]?.cor || "#888")}>
                  {CATEGORIAS[cat]?.emoji} {cat}
                </span>
                <div style={{ textAlign: "right" }}>
                  <span style={{ fontWeight: 700, fontSize: 14 }}>{formatBRL(val)}</span>
                  <span style={{ color: CORES.textoSecundario, fontSize: 12, marginLeft: 8 }}>
                    {saidas > 0 ? (val / saidas * 100).toFixed(1) : 0}%
                  </span>
                </div>
              </div>
              <div style={{ background: CORES.borda, borderRadius: 4, height: 6 }}>
                <div style={{ background: CATEGORIAS[cat]?.cor || "#888", borderRadius: 4, height: "100%", width: `${(val / maxCat) * 100}%`, transition: "width .5s" }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Top 5 */}
      {top5.length > 0 && (
        <div style={S.card}>
          <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>🔝 Top 5 Gastos do Mês</p>
          {top5.map((t, i) => (
            <div key={t.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 0", borderBottom: i < top5.length - 1 ? `1px solid ${CORES.borda}` : "none" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ color: CORES.textoSecundario, fontSize: 13, fontWeight: 700, width: 20 }}>#{i + 1}</span>
                <div>
                  <p style={{ fontWeight: 600, fontSize: 14 }}>{t.descricao}</p>
                  <p style={{ fontSize: 12, color: CORES.textoSecundario }}>{t.subcategoria} · {formatData(t.data)}</p>
                </div>
              </div>
              <span style={{ color: CORES.vermelho, fontWeight: 700, fontSize: 15 }}>{formatBRL(t.valor)}</span>
            </div>
          ))}
        </div>
      )}

      {txMes.length === 0 && (
        <div style={{ ...S.card, textAlign: "center", padding: 40 }}>
          <p style={{ fontSize: 32, marginBottom: 12 }}>📭</p>
          <p style={{ color: CORES.textoSecundario }}>Nenhum lançamento neste mês.</p>
          <p style={{ color: CORES.textoSecundario, fontSize: 13 }}>Acesse "Lançar" para adicionar.</p>
        </div>
      )}
    </div>
  );
}

// ─── LANÇAR ───────────────────────────────────────────────────────────────────
function Lancar({ onSalvar }) {
  const [tipo, setTipo] = useState("SAÍDA");
  const [valor, setValor] = useState("");
  const [data, setData] = useState(hoje.toISOString().split("T")[0]);
  const [descricao, setDescricao] = useState("");
  const [categoria, setCategoria] = useState("");
  const [subcategoria, setSubcategoria] = useState("");
  const [obs, setObs] = useState("");
  const [toast, setToast] = useState(false);
  const [erro, setErro] = useState("");

  const accentColor = tipo === "ENTRADA" ? CORES.verde : CORES.vermelho;

  const handleSalvar = useCallback(() => {
    if (!valor || !descricao || !categoria || !subcategoria || !data) {
      setErro("Preencha todos os campos obrigatórios.");
      return;
    }
    const valorNum = parseFloat(valor.replace(",", "."));
    if (isNaN(valorNum) || valorNum <= 0) { setErro("Valor inválido."); return; }
    const [y, m] = data.split("-");
    onSalvar({ id: gerarId(), mes: parseInt(m), ano: parseInt(y), data, descricao, categoria, subcategoria, valor: valorNum, tipo });
    setValor(""); setDescricao(""); setCategoria(""); setSubcategoria(""); setObs(""); setErro("");
    setToast(true);
    setTimeout(() => setToast(false), 2500);
  }, [valor, data, descricao, categoria, subcategoria, tipo, onSalvar]);

  return (
    <div style={S.secao}>
      {toast && (
        <div style={{ position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)", background: CORES.verde, color: "#000", borderRadius: 10, padding: "12px 24px", fontWeight: 700, zIndex: 200, boxShadow: "0 4px 20px rgba(0,200,150,.4)" }}>
          ✅ Lançamento salvo!
        </div>
      )}

      <div style={{ ...S.card, borderTop: `3px solid ${accentColor}` }}>
        {/* Toggle tipo */}
        <div style={{ display: "flex", background: CORES.bg, borderRadius: 10, padding: 4, marginBottom: 24 }}>
          {["ENTRADA","SAÍDA"].map(t => (
            <button key={t} onClick={() => { setTipo(t); setCategoria(""); setSubcategoria(""); }} style={{
              flex: 1, padding: "10px", borderRadius: 8, border: "none", cursor: "pointer", fontWeight: 700, fontSize: 14, transition: "all .2s",
              background: tipo === t ? (t === "ENTRADA" ? CORES.verde : CORES.vermelho) : "transparent",
              color: tipo === t ? (t === "ENTRADA" ? "#000" : "#fff") : CORES.textoSecundario,
            }}>{t === "ENTRADA" ? "⬆ ENTRADA" : "⬇ SAÍDA"}</button>
          ))}
        </div>

        {/* Valor */}
        <div style={{ marginBottom: 20 }}>
          <label style={S.label}>Valor (R$) *</label>
          <div style={{ position: "relative" }}>
            <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: accentColor, fontWeight: 700, fontSize: 18 }}>R$</span>
            <input value={valor} onChange={e => setValor(e.target.value)} placeholder="0,00"
              style={{ ...S.input, paddingLeft: 46, fontSize: 22, fontWeight: 800, color: accentColor, borderColor: accentColor + "55", height: 56 }} />
          </div>
        </div>

        {/* Data + Descrição */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 12, marginBottom: 20 }}>
          <div>
            <label style={S.label}>Data *</label>
            <input type="date" value={data} onChange={e => setData(e.target.value)} style={S.input} />
          </div>
          <div>
            <label style={S.label}>Descrição *</label>
            <input value={descricao} onChange={e => setDescricao(e.target.value)} placeholder="Ex: Supermercado" style={S.input} />
          </div>
        </div>

        {/* Categoria */}
        <div style={{ marginBottom: 16 }}>
          <label style={S.label}>Categoria *</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8 }}>
            {Object.entries(CATEGORIAS)
              .filter(([c]) => tipo === "ENTRADA" ? c === "RENDA" : c !== "RENDA")
              .map(([cat, info]) => (
                <button key={cat} onClick={() => { setCategoria(cat); setSubcategoria(""); }} style={{
                  background: categoria === cat ? info.cor + "33" : CORES.bg,
                  border: `1px solid ${categoria === cat ? info.cor : CORES.borda}`,
                  borderRadius: 8, padding: "8px 6px", cursor: "pointer", fontSize: 12, fontWeight: 600,
                  color: categoria === cat ? info.cor : CORES.textoSecundario, transition: "all .2s", textAlign: "center"
                }}>{info.emoji} {cat}</button>
              ))}
          </div>
        </div>

        {/* Subcategoria */}
        {categoria && (
          <div style={{ marginBottom: 16 }}>
            <label style={S.label}>Subcategoria *</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              {CATEGORIAS[categoria].sub.map(sub => (
                <button key={sub} onClick={() => setSubcategoria(sub)} style={{
                  background: subcategoria === sub ? CATEGORIAS[categoria].cor + "33" : CORES.bg,
                  border: `1px solid ${subcategoria === sub ? CATEGORIAS[categoria].cor : CORES.borda}`,
                  borderRadius: 6, padding: "6px 12px", cursor: "pointer", fontSize: 12, fontWeight: 600,
                  color: subcategoria === sub ? CATEGORIAS[categoria].cor : CORES.textoSecundario, transition: "all .2s"
                }}>{sub}</button>
              ))}
            </div>
          </div>
        )}

        {/* Observação */}
        <div style={{ marginBottom: 20 }}>
          <label style={S.label}>Observação (opcional)</label>
          <textarea value={obs} onChange={e => setObs(e.target.value)} placeholder="Detalhes adicionais..."
            style={{ ...S.input, resize: "vertical", minHeight: 60 }} />
        </div>

        {erro && <p style={{ color: CORES.vermelho, fontSize: 13, marginBottom: 12 }}>⚠ {erro}</p>}

        <button onClick={handleSalvar} style={{ ...S.btn(accentColor, tipo === "ENTRADA" ? "#000" : "#fff"), width: "100%", padding: "14px", fontSize: 16, borderRadius: 10 }}>
          Salvar Lançamento
        </button>
      </div>
    </div>
  );
}

// ─── HISTÓRICO ────────────────────────────────────────────────────────────────
function Historico({ transacoes, onDeletar }) {
  const [filtroMes, setFiltroMes] = useState(0);
  const [filtroAno, setFiltroAno] = useState(ANO_ATUAL);
  const [filtroCat, setFiltroCat] = useState("Todas");
  const [filtroTipo, setFiltroTipo] = useState("Todos");
  const [busca, setBusca] = useState("");
  const [confirmDelete, setConfirmDelete] = useState(null);

  const filtradas = useMemo(() => {
    return [...transacoes]
      .filter(t => filtroMes === 0 || (t.mes === filtroMes && t.ano === filtroAno))
      .filter(t => filtroCat === "Todas" || t.categoria === filtroCat)
      .filter(t => filtroTipo === "Todos" || t.tipo === filtroTipo)
      .filter(t => !busca || t.descricao.toLowerCase().includes(busca.toLowerCase()))
      .sort((a, b) => b.data.localeCompare(a.data));
  }, [transacoes, filtroMes, filtroAno, filtroCat, filtroTipo, busca]);

  const totalEntradas = filtradas.filter(t => t.tipo === "ENTRADA").reduce((s, t) => s + t.valor, 0);
  const totalSaidas   = filtradas.filter(t => t.tipo === "SAÍDA").reduce((s, t) => s + t.valor, 0);

  const selectStyle = { ...S.input, width: "auto", fontSize: 13, padding: "8px 12px" };

  return (
    <div style={S.secao}>
      {confirmDelete && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 200 }}>
          <div style={{ ...S.card, maxWidth: 320, width: "90%", textAlign: "center" }}>
            <p style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>Excluir lançamento?</p>
            <p style={{ color: CORES.textoSecundario, fontSize: 14, marginBottom: 20 }}>{confirmDelete.descricao}</p>
            <div style={{ display: "flex", gap: 10 }}>
              <button onClick={() => setConfirmDelete(null)} style={{ ...S.btn(CORES.card), flex: 1, border: `1px solid ${CORES.borda}` }}>Cancelar</button>
              <button onClick={() => { onDeletar(confirmDelete.id); setConfirmDelete(null); }} style={{ ...S.btn(CORES.vermelho), flex: 1 }}>Excluir</button>
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div style={{ ...S.card, marginBottom: 16 }}>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 10 }}>
          <select value={filtroMes} onChange={e => setFiltroMes(Number(e.target.value))} style={selectStyle}>
            <option value={0}>Todos os meses</option>
            {MESES_NOMES.map((m, i) => <option key={i} value={i + 1}>{m} {filtroAno}</option>)}
          </select>
          <select value={filtroCat} onChange={e => setFiltroCat(e.target.value)} style={selectStyle}>
            <option>Todas</option>
            {Object.keys(CATEGORIAS).map(c => <option key={c}>{c}</option>)}
          </select>
          <select value={filtroTipo} onChange={e => setFiltroTipo(e.target.value)} style={selectStyle}>
            {["Todos","ENTRADA","SAÍDA"].map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <input value={busca} onChange={e => setBusca(e.target.value)} placeholder="🔍 Buscar por descrição..." style={S.input} />
      </div>

      {/* Lista */}
      <div style={S.card}>
        {filtradas.length === 0 ? (
          <p style={{ color: CORES.textoSecundario, textAlign: "center", padding: 30 }}>Nenhum lançamento encontrado.</p>
        ) : (
          filtradas.map((t, i) => (
            <div key={t.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "12px 0", borderBottom: i < filtradas.length - 1 ? `1px solid ${CORES.borda}` : "none" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1, minWidth: 0 }}>
                <span style={{ ...S.badge(CATEGORIAS[t.categoria]?.cor || "#888"), flexShrink: 0, fontSize: 11 }}>
                  {CATEGORIAS[t.categoria]?.emoji}
                </span>
                <div style={{ minWidth: 0 }}>
                  <p style={{ fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{t.descricao}</p>
                  <p style={{ fontSize: 12, color: CORES.textoSecundario }}>{t.subcategoria} · {formatData(t.data)}</p>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
                <span style={{ color: t.tipo === "ENTRADA" ? CORES.verde : CORES.vermelho, fontWeight: 700, fontSize: 14 }}>
                  {t.tipo === "ENTRADA" ? "+" : "-"}{formatBRL(t.valor)}
                </span>
                <button onClick={() => setConfirmDelete(t)} style={{ background: "none", border: "none", cursor: "pointer", color: CORES.textoSecundario, fontSize: 16, padding: 4 }}>🗑</button>
              </div>
            </div>
          ))
        )}

        {/* Rodapé */}
        {filtradas.length > 0 && (
          <div style={{ display: "flex", justifyContent: "space-between", paddingTop: 14, marginTop: 4, borderTop: `1px solid ${CORES.borda}` }}>
            <span style={{ color: CORES.verde, fontWeight: 600, fontSize: 13 }}>Entradas: {formatBRL(totalEntradas)}</span>
            <span style={{ color: CORES.vermelho, fontWeight: 600, fontSize: 13 }}>Saídas: {formatBRL(totalSaidas)}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── EVOLUÇÃO ─────────────────────────────────────────────────────────────────
function Evolucao({ transacoes, metaCarro }) {
  const [ano, setAno] = useState(ANO_ATUAL);

  const dadosMensais = useMemo(() => {
    return MESES_NOMES.map((nome, i) => {
      const m = i + 1;
      const txM = transacoes.filter(t => t.mes === m && t.ano === ano);
      const entradas = txM.filter(t => t.tipo === "ENTRADA").reduce((s, t) => s + t.valor, 0);
      const saidas   = txM.filter(t => t.tipo === "SAÍDA").reduce((s, t) => s + t.valor, 0);
      return { nome, entradas, saidas, saldo: entradas - saidas };
    });
  }, [transacoes, ano]);

  const dadosCategoria = useMemo(() => {
    const acc = {};
    transacoes.filter(t => t.ano === ano && t.tipo === "SAÍDA").forEach(t => {
      acc[t.categoria] = (acc[t.categoria] || 0) + t.valor;
    });
    return Object.entries(acc).map(([cat, val]) => ({ nome: cat, valor: val, cor: CATEGORIAS[cat]?.cor || "#888" })).sort((a, b) => b.valor - a.valor);
  }, [transacoes, ano]);

  const dadosCarro = useMemo(() => {
    let acum = metaCarro.jaGuardado;
    return MESES_NOMES.map((nome, i) => {
      const m = i + 1;
      const reserva = transacoes.filter(t => t.mes === m && t.ano === ano && t.categoria === "META CARRO").reduce((s, t) => s + t.valor, 0);
      acum += reserva;
      return { nome, acumulado: acum };
    });
  }, [transacoes, ano, metaCarro]);

  const totalAnual = dadosMensais.reduce((s, m) => ({ entradas: s.entradas + m.entradas, saidas: s.saidas + m.saidas }), { entradas: 0, saidas: 0 });
  const saldoAnual = totalAnual.entradas - totalAnual.saidas;

  return (
    <div style={S.secao}>
      {/* Seletor ano */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, fontWeight: 800 }}>📈 Evolução Anual</h2>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button onClick={() => setAno(a => a - 1)} style={{ ...S.btn(CORES.card), padding: "6px 12px", border: `1px solid ${CORES.borda}` }}>‹</button>
          <span style={{ fontWeight: 700, fontSize: 16, minWidth: 48, textAlign: "center" }}>{ano}</span>
          <button onClick={() => setAno(a => a + 1)} style={{ ...S.btn(CORES.card), padding: "6px 12px", border: `1px solid ${CORES.borda}` }}>›</button>
        </div>
      </div>

      {/* Resumo anual */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 24 }}>
        {[
          { label: "Entradas Anuais", valor: totalAnual.entradas, cor: CORES.verde },
          { label: "Saídas Anuais",   valor: totalAnual.saidas,   cor: CORES.vermelho },
          { label: "Saldo do Ano",    valor: saldoAnual,          cor: saldoAnual >= 0 ? CORES.verde : CORES.vermelho },
        ].map((c, i) => (
          <div key={i} style={{ ...S.card, textAlign: "center" }}>
            <p style={{ fontSize: 10, color: CORES.textoSecundario, marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>{c.label}</p>
            <p style={{ fontSize: 15, fontWeight: 800, color: c.cor }}>{formatBRL(c.valor)}</p>
          </div>
        ))}
      </div>

      {/* Gráfico 1 — Entradas vs Saídas */}
      <div style={{ ...S.card, marginBottom: 20 }}>
        <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>Entradas vs Saídas — Ano Completo</p>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={dadosMensais} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CORES.borda} />
            <XAxis dataKey="nome" tick={{ fill: CORES.textoSecundario, fontSize: 11 }} />
            <YAxis tick={{ fill: CORES.textoSecundario, fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<TooltipCustom />} />
            <Legend wrapperStyle={{ color: CORES.textoSecundario, fontSize: 12 }} />
            <Bar dataKey="entradas" name="Entradas" fill={CORES.verde} radius={[4, 4, 0, 0]} />
            <Bar dataKey="saidas"   name="Saídas"   fill={CORES.vermelho} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico 2 — Saldo mensal */}
      <div style={{ ...S.card, marginBottom: 20 }}>
        <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>Saldo Mensal</p>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={dadosMensais} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gradSaldo" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CORES.verde} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CORES.verde} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={CORES.borda} />
            <XAxis dataKey="nome" tick={{ fill: CORES.textoSecundario, fontSize: 11 }} />
            <YAxis tick={{ fill: CORES.textoSecundario, fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<TooltipCustom />} />
            <ReferenceLine y={0} stroke={CORES.vermelho} strokeDasharray="4 4" />
            <Area type="monotone" dataKey="saldo" name="Saldo" stroke={CORES.verde} fill="url(#gradSaldo)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico 3 — Por categoria */}
      {dadosCategoria.length > 0 && (
        <div style={{ ...S.card, marginBottom: 20 }}>
          <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>Distribuição Anual por Categoria</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={dadosCategoria} layout="vertical" margin={{ top: 5, right: 60, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={CORES.borda} horizontal={false} />
              <XAxis type="number" tick={{ fill: CORES.textoSecundario, fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="nome" tick={{ fill: CORES.textoSecundario, fontSize: 11 }} width={130} />
              <Tooltip content={<TooltipCustom />} />
              <Bar dataKey="valor" name="Total" radius={[0, 4, 4, 0]}>
                {dadosCategoria.map((entry, i) => <Cell key={i} fill={entry.cor} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Gráfico 4 — Meta carro */}
      <div style={S.card}>
        <p style={{ fontWeight: 700, marginBottom: 16, fontSize: 15 }}>Progresso da Meta — Carro</p>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={dadosCarro} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gradCarro" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CORES.ambar} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CORES.ambar} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={CORES.borda} />
            <XAxis dataKey="nome" tick={{ fill: CORES.textoSecundario, fontSize: 11 }} />
            <YAxis tick={{ fill: CORES.textoSecundario, fontSize: 10 }} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
            <Tooltip content={<TooltipCustom />} />
            <ReferenceLine y={metaCarro.precoAlvo} stroke={CORES.ambar} strokeDasharray="6 3" label={{ value: "Meta", position: "right", fill: CORES.ambar, fontSize: 11 }} />
            <Area type="monotone" dataKey="acumulado" name="Acumulado" stroke={CORES.ambar} fill="url(#gradCarro)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// ─── META CARRO ───────────────────────────────────────────────────────────────
function MetaCarro({ metaCarro, setMetaCarro, transacoes }) {
  const { precoAlvo, jaGuardado, metaMensal } = metaCarro;
  const [rendaExtra, setRendaExtra] = useState(0);

  const totalMensal = metaMensal + rendaExtra;
  const falta = Math.max(0, precoAlvo - jaGuardado);
  const mesesRestantes = totalMensal > 0 ? Math.ceil(falta / totalMensal) : 999;
  const pct = precoAlvo > 0 ? Math.min((jaGuardado / precoAlvo) * 100, 100) : 0;

  const prazoEstimado = () => {
    if (mesesRestantes >= 999) return "—";
    const d = new Date(hoje.getFullYear(), hoje.getMonth() + mesesRestantes, 1);
    return `${MESES_COMPLETOS[d.getMonth()]} / ${d.getFullYear()}`;
  };

  const reservadoEstesMes = transacoes.filter(t => t.mes === MES_ATUAL && t.ano === ANO_ATUAL && t.categoria === "META CARRO").reduce((s, t) => s + t.valor, 0);

  const projecao = useMemo(() => {
    let acum = jaGuardado;
    return Array.from({ length: 24 }, (_, i) => {
      acum += totalMensal;
      const pctMes = precoAlvo > 0 ? Math.min((acum / precoAlvo) * 100, 100) : 0;
      const status = acum >= precoAlvo ? "✅ META!" : pctMes >= 75 ? "🟡 75%+" : pctMes >= 50 ? "🔵 50%+" : "⏳ Acumulando";
      return { mes: `Mês ${i + 1}`, reserva: totalMensal, acumulado: acum, pct: pctMes, status };
    });
  }, [jaGuardado, totalMensal, precoAlvo]);

  const inputMeta = { ...S.input, textAlign: "right", fontWeight: 700 };

  return (
    <div style={S.secao}>
      <div style={{ ...S.card, borderTop: `3px solid ${CORES.ambar}`, marginBottom: 20 }}>
        <p style={{ fontWeight: 800, fontSize: 16, marginBottom: 20 }}>🚘 Configurar Meta</p>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
          {[
            { label: "Preço-alvo do carro (R$)", key: "precoAlvo" },
            { label: "Já guardado hoje (R$)",    key: "jaGuardado" },
            { label: "Meta mensal de reserva (R$)", key: "metaMensal" },
          ].map(({ label, key }) => (
            <div key={key}>
              <label style={S.label}>{label}</label>
              <input type="number" value={metaCarro[key]}
                onChange={e => setMetaCarro(m => ({ ...m, [key]: parseFloat(e.target.value) || 0 }))}
                style={inputMeta} />
            </div>
          ))}
          <div>
            <label style={S.label}>Renda extra esperada/mês (R$)</label>
            <input type="number" value={rendaExtra} onChange={e => setRendaExtra(parseFloat(e.target.value) || 0)} style={inputMeta} />
          </div>
        </div>
      </div>

      {/* Barra de progresso */}
      <div style={{ ...S.card, marginBottom: 20, textAlign: "center" }}>
        <p style={{ fontSize: 14, color: CORES.textoSecundario, marginBottom: 10 }}>
          {formatBRL(jaGuardado)} de {formatBRL(precoAlvo)} — <strong style={{ color: CORES.ambar }}>{pct.toFixed(1)}% concluído</strong>
        </p>
        <div style={{ background: CORES.borda, borderRadius: 10, height: 20, overflow: "hidden", marginBottom: 20 }}>
          <div style={{ background: `linear-gradient(90deg, ${CORES.ambar}, #FFD700)`, height: "100%", width: `${pct}%`, borderRadius: 10, transition: "width 0.8s ease" }} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
          {[
            { label: "Falta guardar",    valor: formatBRL(falta),         cor: CORES.vermelho },
            { label: "Meses restantes",  valor: mesesRestantes >= 999 ? "—" : `${mesesRestantes} meses`, cor: CORES.ambar },
            { label: "Prazo estimado",   valor: prazoEstimado(),           cor: CORES.verde },
          ].map((c, i) => (
            <div key={i} style={{ background: CORES.bg, borderRadius: 10, padding: 12 }}>
              <p style={{ fontSize: 10, color: CORES.textoSecundario, marginBottom: 4, textTransform: "uppercase" }}>{c.label}</p>
              <p style={{ fontWeight: 800, fontSize: 14, color: c.cor }}>{c.valor}</p>
            </div>
          ))}
        </div>

        {/* Dica motivacional */}
        <div style={{ marginTop: 16, padding: "10px 14px", background: CORES.bg, borderRadius: 10, textAlign: "left" }}>
          {rendaExtra > 0 && <p style={{ fontSize: 13, color: CORES.verde }}>💡 Com sua renda extra, você adianta aprox. {Math.floor(falta / totalMensal - falta / metaMensal)} meses!</p>}
          {reservadoEstesMes >= metaMensal && <p style={{ fontSize: 13, color: CORES.verde }}>🎯 No ritmo certo este mês!</p>}
          {reservadoEstesMes < metaMensal && reservadoEstesMes > 0 && <p style={{ fontSize: 13, color: CORES.ambar }}>⚠ Reserva deste mês abaixo da meta ({formatBRL(metaMensal - reservadoEstesMes)} a mais).</p>}
          {reservadoEstesMes === 0 && <p style={{ fontSize: 13, color: CORES.vermelho }}>⚠ Este mês faltou lançar a reserva do carro.</p>}
        </div>
      </div>

      {/* Tabela projeção */}
      <div style={S.card}>
        <p style={{ fontWeight: 700, marginBottom: 14, fontSize: 15 }}>📆 Projeção 24 Meses</p>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr>
                {["Mês","Reserva","Acumulado","% Meta","Status"].map(h => (
                  <th key={h} style={{ padding: "8px 10px", textAlign: "left", color: CORES.textoSecundario, fontSize: 11, textTransform: "uppercase", borderBottom: `1px solid ${CORES.borda}` }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {projecao.map((p, i) => (
                <tr key={i} style={{ background: i % 2 === 0 ? "transparent" : CORES.bg + "88" }}>
                  <td style={{ padding: "8px 10px", color: CORES.textoSecundario }}>{p.mes}</td>
                  <td style={{ padding: "8px 10px" }}>{formatBRL(p.reserva)}</td>
                  <td style={{ padding: "8px 10px", color: CORES.ambar, fontWeight: 600 }}>{formatBRL(p.acumulado)}</td>
                  <td style={{ padding: "8px 10px" }}>{p.pct.toFixed(1)}%</td>
                  <td style={{ padding: "8px 10px" }}>{p.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── APP PRINCIPAL ────────────────────────────────────────────────────────────
export default function App() {
  const [aba, setAba]               = useState("painel");
  const [transacoes, setTransacoes] = useState(DADOS_EXEMPLO);
  const [mes, setMes]               = useState(MES_ATUAL);
  const [ano, setAno]               = useState(ANO_ATUAL);
  const [metaCarro, setMetaCarro]   = useState({ precoAlvo: 40000, jaGuardado: 0, metaMensal: 500 });

  const handleSalvar  = useCallback((t) => setTransacoes(prev => [...prev, t]), []);
  const handleDeletar = useCallback((id) => setTransacoes(prev => prev.filter(t => t.id !== id)), []);

  const navItems = [
    { id: "painel",    emoji: "📊", label: "Painel" },
    { id: "lancar",    emoji: "➕", label: "Lançar" },
    { id: "historico", emoji: "🧾", label: "Histórico" },
    { id: "evolucao",  emoji: "📈", label: "Evolução" },
    { id: "meta",      emoji: "🚘", label: "Meta" },
  ];

  return (
    <div style={S.app}>
      {/* Header */}
      <div style={{ background: CORES.card, borderBottom: `1px solid ${CORES.borda}`, padding: "14px 20px", position: "sticky", top: 0, zIndex: 50 }}>
        <div style={{ maxWidth: 800, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <p style={{ fontSize: 10, color: CORES.textoSecundario, textTransform: "uppercase", letterSpacing: "0.1em" }}>Dashboard</p>
            <h1 style={{ fontSize: 18, fontWeight: 900, color: CORES.verde, letterSpacing: "-0.02em" }}>Controle Financeiro</h1>
          </div>
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: 11, color: CORES.textoSecundario }}>{MESES_COMPLETOS[mes - 1]}</p>
            <p style={{ fontSize: 14, fontWeight: 700 }}>{ano}</p>
          </div>
        </div>
      </div>

      {/* Conteúdo */}
      {aba === "painel"    && <Painel    transacoes={transacoes} mes={mes} ano={ano} setMes={setMes} setAno={setAno} />}
      {aba === "lancar"    && <Lancar    onSalvar={handleSalvar} />}
      {aba === "historico" && <Historico transacoes={transacoes} onDeletar={handleDeletar} />}
      {aba === "evolucao"  && <Evolucao  transacoes={transacoes} metaCarro={metaCarro} />}
      {aba === "meta"      && <MetaCarro metaCarro={metaCarro} setMetaCarro={setMetaCarro} transacoes={transacoes} />}

      {/* Nav */}
      <nav style={S.nav}>
        {navItems.map(item => (
          <button key={item.id} onClick={() => setAba(item.id)} style={S.navItem(aba === item.id)}>
            <span style={{ fontSize: 20 }}>{item.emoji}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
}
