# -*- coding: utf-8 -*-
u"""
============================================================
 O PAINEL DE LINKS — gerado do `ATIVIDADES.md`, nunca à mão.

 Pedido do Marcos (set/2026): *"preciso de um tipo de painel onde eu tenho o
 nome da atividade, a turma, o que é trabalhado nessa atividade de forma
 resumida e o link, pq às vezes eu preciso rápido do link e vc demora para me
 passar, pode até ser organizado por turma"*.

 ⭐ POR QUE GERADO, e não escrito à mão: um painel escrito à mão vira mentira na
 primeira atividade nova — e aí ele volta a me pedir o link, que é exatamente o
 atrito que este painel existe para acabar. O `ATIVIDADES.md` já é a FONTE ÚNICA
 DA VERDADE da casa (decisão dele, ago/2026: *"crie um documento no git, sempre
 que criar uma atividade insira nessa tabela o ano, o nome da atividade, o que
 ela trabalha e o link"*). Então o painel se gera dali: uma linha nova no
 catálogo vira um cartão novo no painel, sem eu tocar em HTML.

 Uso:  python3 _painel/montar_painel.py
       (lê ../ATIVIDADES.md e escreve _painel/index.html)
============================================================
"""
import io
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CATALOGO = os.path.join(RAIZ, "ATIVIDADES.md")
SAIDA = os.path.join(AQUI, "index.html")

# a ordem em que as turmas aparecem — a ordem da escola, não a alfabética
ORDEM = [u"Pré-escola", u"1º ano", u"2º ano", u"3º ano", u"4º ano", u"5º ano",
         u"6º ano", u"7º ano", u"8º ano", u"9º ano", u"Inglês", u"Outras",
         u"Portal"]


def curto(turma):
    u"""o rótulo do chip: '3º', 'Pré', 'Inglês'"""
    m = re.match(r"(\d)[ºo°]", turma)
    if m:
        return m.group(1) + u"º"
    if turma.startswith(u"Pré"):
        return u"Pré"
    if u"Inglês" in turma or u"ano (Inglês)" in turma:
        return u"Inglês"
    if turma.startswith(u"Portal"):
        return u"Portal"
    return u"Outras"


def posicao(turma):
    for i, o in enumerate(ORDEM):
        if turma.startswith(o) or o in turma:
            return i
    return len(ORDEM)


def links_da_celula(cel):
    u"""a célula de link pode trazer o link da atividade E o do painel do
    professor: `https://a/ · [painel](https://b/)`. Devolve os dois."""
    painel = None
    m = re.search(r"\[painel\]\((https?://[^\)]+)\)", cel)
    if m:
        painel = m.group(1)
        cel = cel[:m.start()] + cel[m.end():]
    urls = re.findall(r"https?://[^\s·\)\]]+", cel)
    principal = urls[0].rstrip(".,") if urls else None
    return principal, painel


def le_catalogo():
    if not os.path.exists(CATALOGO):
        print(u"NAO MEDI: nao achei %s" % CATALOGO)
        return None
    linhas = io.open(CATALOGO, encoding="utf-8").read().splitlines()
    turma, itens = None, []
    for ln in linhas:
        h = re.match(r"^##\s+(.+?)\s*$", ln)
        if h:
            turma = h.group(1).strip()
            continue
        if not turma or not ln.startswith("|"):
            continue
        cels = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cels) < 4:
            continue
        nome = re.sub(r"\*\*", "", cels[0]).strip()
        if not nome or nome in ("Atividade", "—") or set(nome) <= set("-: "):
            continue
        trabalha = re.sub(r"\*\*", "", cels[1]).strip()
        pasta = re.sub(r"`", "", cels[2]).strip()
        link, painel = links_da_celula(cels[3])
        itens.append({
            "turma": turma, "chip": curto(turma), "pos": posicao(turma),
            "nome": nome,
            "trabalha": u"" if trabalha in (u"—", u"-") else trabalha,
            "pasta": u"" if pasta in (u"—", u"-") else pasta,
            "link": link or u"", "painel": painel or u"",
        })
    return itens


PAGINA = u"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Atividades — E.B.M. Vidal Ramos</title>
<meta name="theme-color" content="#1d3557">
<style>
:root{
  --fundo:#f4f1ec; --papel:#fffdfa; --tinta:#22201c; --fraco:#6b6459;
  --linha:#e3ddd2; --azul:#1d3557; --azul-c:#2a4d78; --ok:#2f7d52;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--fundo);color:var(--tinta);
  font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  -webkit-text-size-adjust:100%}
header{position:sticky;top:0;z-index:10;background:var(--azul);color:#fff;
  padding:10px 12px calc(10px + env(safe-area-inset-bottom,0px));
  box-shadow:0 2px 10px rgba(0,0,0,.18)}
h1{margin:0 0 8px;font-size:17px;letter-spacing:.2px}
h1 small{display:block;font-weight:400;font-size:12px;opacity:.8;letter-spacing:0}
#busca{width:100%;padding:11px 12px;border:0;border-radius:10px;font-size:16px;
  background:#fff;color:var(--tinta)}
#chips{display:flex;gap:6px;overflow-x:auto;padding:8px 0 2px;
  -webkit-overflow-scrolling:touch;scrollbar-width:none}
#chips::-webkit-scrollbar{display:none}
.chip{flex:0 0 auto;border:1px solid rgba(255,255,255,.45);background:transparent;
  color:#fff;border-radius:99px;padding:0 15px;min-height:40px;font-size:14.5px;
  font-weight:600;cursor:pointer}
  /* ⚠️ 40px é o piso da casa para alvo de dedo (o `_qa/leiaute.js` reprova
     abaixo disso). Com `padding:6px` os chips davam 31px e o Marcos erraria a
     turma no celular — justamente o gesto que ele mais vai usar aqui. */
.chip[aria-pressed="true"]{background:#fff;color:var(--azul);border-color:#fff}
main{padding:12px 12px 40px;max-width:820px;margin:0 auto}
/* ⭐ O CONTROLE DA SALA AO LADO (pedido do Marcos, set/2026: *"tem como o
   controle da sala ser no mesmo painel de atividades?... é mais fácil para
   copiar e colar os links"* e *"o painel de controle é bem pequeno, daria para
   ficar à direita do outro painel, pq tem espaço"*).

   Ele COPIA o link de uma atividade aqui e COLA no controle para mandar às
   máquinas da sala. Eram duas abas; agora é uma tela: lista à esquerda,
   controle à direita.

   ⚠️ O CONTROLE NÃO MUDA UMA LINHA. Ele entra por `<iframe>` apontando para o
   endereço dele mesmo (`controle-lab/controle.html`), que continua funcionando
   sozinho, no mesmo link de sempre. Duas coisas tornam isso seguro, e as duas
   foram conferidas no arquivo dele:
     · o `controle.html` não tem NENHUMA chamada que navegue a janela
       (`window.top`, `location.href=`, `window.open`) — quem tem é o
       `index.html`, que é a tela da MÁQUINA DO ALUNO, e essa não entra aqui;
     · painel e controle moram no MESMO domínio (vidalprof.github.io), então já
       hoje dividem o mesmo localStorage: embutir não muda nada nisso.
   Ele já nasce estreito (`max-width:460px` no CSS dele) — cabe na faixa. */
#corpo{display:block}
#sala{display:none}
#btsala{display:none}
/* ⚠️ O CORTE É 980px, não 1040: o netbook da escola tem 1024 de largura, e é
   justamente nele que ele usa o controle. Com 1040 a coluna sumiria lá. Em 1024
   a faixa fica com 430px (o controle já nasce com max-width:460) e a lista com
   o resto — medido, sem rolagem lateral. */
@media (min-width:980px){
  /* a página inteira vira aplicativo: o cabeçalho fica, e só a LISTA rola.
     Assim o controle da direita não sai da tela quando ele procura a atividade. */
  html,body{height:100%}
  body{display:-webkit-box;display:flex;-webkit-box-orient:vertical;
    flex-direction:column;overflow:hidden}
  header{position:static;-webkit-box-flex:0;flex:0 0 auto}
  /* ⚠️ SEM `max-width` E SEM `margin:0 auto` — de propósito (pedido do Marcos,
     set/2026: *"pode jogar a lista de atividades mais pra esquerda, bem no
     começo, assim sobra mais espaço para o painel e a lista que vc citou"*).
     Antes o conteúdo era uma coluna de 1460px CENTRADA: num monitor de 1920 isso
     jogava 230px de vazio de cada lado e empurrava a lista para o meio da tela.
     Agora a lista começa na borda esquerda (só o respiro de 10px) e TODA a
     largura da tela é dividida entre lista e controle. */
  #corpo{-webkit-box-flex:1;flex:1 1 auto;display:-webkit-box;display:flex;
    min-height:0;gap:14px;margin:0;width:100%;padding:12px 12px 12px 10px}
  main{-webkit-box-flex:1;flex:1 1 auto;min-height:0;overflow-y:auto;
    max-width:none;padding:0 4px 24px;margin:0}
  #sala{display:-webkit-box;display:flex;-webkit-box-orient:vertical;
    flex-direction:column;-webkit-box-flex:0;flex:0 0 430px;min-height:0}
  #sala h3{margin:0 0 7px;font-size:13px;text-transform:uppercase;
    letter-spacing:1px;color:var(--fraco);font-weight:700}
  #sala h3 a{color:var(--azul-c);text-decoration:none;font-size:12px;
    text-transform:none;letter-spacing:0;float:right;font-weight:600}
  #sala iframe{-webkit-box-flex:1;flex:1 1 auto;width:100%;border:0;
    border-radius:14px;background:#0c1730;
    -webkit-box-shadow:0 4px 14px rgba(90,60,20,.16);
    box-shadow:0 4px 14px rgba(90,60,20,.16)}
}
/* ⚠️ TELA BAIXA (o netbook de 600px de altura): o cabeçalho comia 172 dos 600,
   e sobravam 416 para a lista E para o controle. Cada pixel tirado daqui vira
   pixel útil nos dois. Mesma lição do Pinta e Monta. */
@media (min-width:980px) and (max-height:700px){
  header{padding:6px 12px}
  h1{font-size:15px;margin-bottom:5px}
  h1 small{font-size:11px}
  #busca{padding:11px 12px;font-size:15px;min-height:40px}
  #chips{padding:6px 0 0}
  .chip{padding:0 12px}      /* mais estreito, mas os 40px de ALTURA ficam */
  #corpo{padding:8px 12px 8px 10px}
  .card{padding:9px 11px;margin-bottom:7px}
  .trab{margin-bottom:7px}
}
/* ⚠️ E o que eu NÃO encolhi, de propósito: a ALTURA dos chips e dos botões.
   Na primeira tentativa apertei os dois e ganhei 34px — ao preço de 12 alvos
   abaixo dos 40px que a casa exige para o dedo. Espaço se tira do título e do
   respiro, nunca do que a pessoa precisa acertar. */
/* ⚠️ O CONTROLE NÃO GANHA MAIS DO QUE USA (ajuste do Marcos: *"redistribua
   melhor a tela"*). O CSS dele é `max-width:460px` — dar 560 desperdiçava 100px
   de faixa vazia enquanto a lista de atividades ficava apertada. O teto é 470
   (460 + a folga da barra de rolagem); daí para cima, tudo o que sobra vai para
   as atividades, que é onde ele procura e copia. */
@media (min-width:1200px){ #sala{-webkit-box-flex:0;flex:0 0 470px} }
/* ⭐ E no monitor grande o controle CRESCE de verdade (não é faixa vazia): o
   `.wrap` do próprio `controle.html` passou a 560px, então a partir de 1520 de
   largura a coluna vai a 580 e o controle usa isso — campo do alvo mais largo,
   botões maiores e a lista "JÁ TERMINARAM" cabendo numa linha só. */
@media (min-width:1520px){ #sala{-webkit-box-flex:0;flex:0 0 580px} }
/* ⚠️ A LISTA É UMA COLUNA VERTICAL — e isso é escolha, não sobra.
   Eu tinha posto a lista em GRADE de 2/3 colunas no monitor grande, achando que
   ver 15 atividades de uma vez ajudaria. O Marcos olhou e disse: *"acho que
   você podia deixar a lista da esquerda como estava, na vertical, desse jeito
   ocupa muito espaço"*. Ele tem razão pelo uso real: ele varre a coluna de cima
   para baixo procurando UMA atividade e copia o link — a grade obriga o olho a
   ziguezaguear e espalha a divisão por turma.
   Então a coluna volta, e a largura que sobra no monitor grande vai para o
   CONTROLE (que é o que ele usa ao lado), não para esticar cartão. */
@media (min-width:1360px){
  main{max-width:700px}                 /* a coluna de leitura, encostada à esquerda */
  /* ⚠️ e o controle OCUPA o resto, em vez de deixar um vazio claro do lado
     direito: com as duas colunas travadas sobrava meia tela de fundo liso, que
     lê como página quebrada. O `.wrap` do controle vai até 720px, então ele
     cresce de verdade dentro dessa faixa (campo e botões maiores). */
  #sala{-webkit-box-flex:1;flex:1 1 auto;min-width:0}
}
h2{font-size:13px;text-transform:uppercase;letter-spacing:1px;color:var(--fraco);
  margin:20px 0 8px;font-weight:700}
h2:first-of-type{margin-top:4px}
.card{background:var(--papel);border:1px solid var(--linha);border-radius:12px;
  padding:11px 12px;margin-bottom:9px}
.nome{font-weight:700;font-size:16px;margin-bottom:2px}
.trab{color:var(--fraco);font-size:13.5px;margin-bottom:9px}
.acoes{display:flex;gap:7px;flex-wrap:wrap}
.bt{flex:1 1 auto;min-width:120px;text-align:center;text-decoration:none;
  border:1px solid var(--linha);border-radius:9px;padding:11px 10px;
  font-size:14.5px;font-weight:700;cursor:pointer;background:#fff;color:var(--azul)}
.bt.abrir{background:var(--azul);color:#fff;border-color:var(--azul)}
.bt.prof{flex:0 0 auto;min-width:0;color:var(--azul-c)}
.bt.copiado{background:var(--ok);color:#fff;border-color:var(--ok)}
.semlink{color:var(--fraco);font-size:13.5px;font-style:italic}
#vazio{display:none;text-align:center;color:var(--fraco);padding:30px 10px}
#rodape{color:var(--fraco);font-size:12px;text-align:center;margin-top:22px}
@media (min-width:640px){ .bt{flex:0 0 auto;min-width:150px} }
</style>
</head>
<body>
<header>
  <h1>Atividades <small>E.B.M. Vidal Ramos &middot; @@TOTAL@@ atividades &middot; toque em COPIAR para pegar o link</small></h1>
  <input id="busca" type="search" placeholder="Buscar por nome ou pelo que trabalha…" autocomplete="off">
  <div id="chips"></div>
</header>
<div id="corpo">
  <main>
    <div id="lista"></div>
    <p id="vazio">Nada com esse nome. Tente outra palavra.</p>
    <p id="rodape">Gerado do catálogo do projeto &middot; @@QUANDO@@</p>
  </main>
  <aside id="sala">
    <h3>Controle da sala<a href="https://vidalprof.github.io/controle-lab/controle.html" target="_blank" rel="noopener">abrir sozinho &rsaquo;</a></h3>
    <iframe id="ifsala" title="Controle do Laborat&oacute;rio" loading="lazy"
      src="https://vidalprof.github.io/controle-lab/controle.html"></iframe>
  </aside>
</div>
<script>
var DADOS = @@DADOS@@;

function esc(s){ var d=document.createElement("div"); d.textContent=s==null?"":s; return d.innerHTML; }

/* ⚠️ COPIAR TEM DE FUNCIONAR NO CELULAR DA ESCOLA, e o `navigator.clipboard` só
   existe em https (ou localhost). Como o painel abre por https no Pages, o
   caminho normal funciona — mas se um dia ele abrir de outro jeito, o
   `execCommand` antigo salva. Sem o segundo caminho, o botão faria NADA e ele
   voltaria a me pedir o link, que é o problema que este painel resolve. */
function copiar(txt, bt){
  function feito(){
    var antes=bt.textContent; bt.textContent="✓ Copiado!"; bt.className="bt copiado";
    setTimeout(function(){ bt.textContent=antes; bt.className="bt"; }, 1600);
  }
  try{
    if(navigator.clipboard && navigator.clipboard.writeText){
      navigator.clipboard.writeText(txt).then(feito, function(){ velho(txt,feito); });
      return;
    }
  }catch(e){}
  velho(txt, feito);
}
function velho(txt, feito){
  try{
    var t=document.createElement("textarea");
    t.value=txt; t.setAttribute("readonly","");
    t.style.position="fixed"; t.style.left="-9999px";
    document.body.appendChild(t); t.select(); t.setSelectionRange(0,99999);
    var ok=document.execCommand("copy"); document.body.removeChild(t);
    if(ok){ feito(); return; }
  }catch(e){}
  window.prompt("Copie o link:", txt);
}

var filtro="", turmaAtiva="";

function turmas(){
  var vistas=[], i;
  for(i=0;i<DADOS.length;i++) if(vistas.indexOf(DADOS[i].chip)<0) vistas.push(DADOS[i].chip);
  return vistas;
}

function desenhaChips(){
  var c=document.getElementById("chips"), ts=turmas(), h="";
  h+='<button class="chip" data-t="" aria-pressed="'+(turmaAtiva===""?"true":"false")+'">Todas</button>';
  for(var i=0;i<ts.length;i++)
    h+='<button class="chip" data-t="'+esc(ts[i])+'" aria-pressed="'+(turmaAtiva===ts[i]?"true":"false")+'">'+esc(ts[i])+'</button>';
  c.innerHTML=h;
  var bs=c.getElementsByClassName("chip");
  for(var j=0;j<bs.length;j++) bs[j].onclick=function(){
    turmaAtiva=this.getAttribute("data-t"); desenhaChips(); desenha();
  };
}

function desenha(){
  var alvo=document.getElementById("lista"), h="", turmaAnterior=null, n=0;
  var q=filtro.toLowerCase();
  for(var i=0;i<DADOS.length;i++){
    var a=DADOS[i];
    if(turmaAtiva && a.chip!==turmaAtiva) continue;
    if(q && (a.nome+" "+a.trabalha+" "+a.turma).toLowerCase().indexOf(q)<0) continue;
    n++;
    if(a.turma!==turmaAnterior){ h+="<h2>"+esc(a.turma)+"</h2>"; turmaAnterior=a.turma; }
    h+='<div class="card"><div class="nome">'+esc(a.nome)+'</div>';
    if(a.trabalha) h+='<div class="trab">'+esc(a.trabalha)+'</div>';
    h+='<div class="acoes">';
    if(a.link){
      h+='<a class="bt abrir" href="'+esc(a.link)+'" target="_blank" rel="noopener">Abrir</a>';
      h+='<button class="bt" data-copiar="'+esc(a.link)+'">Copiar link</button>';
      if(a.painel) h+='<a class="bt prof" href="'+esc(a.painel)+'" target="_blank" rel="noopener">Painel do professor</a>';
    }else{
      h+='<span class="semlink">ainda não publicada</span>';
    }
    h+="</div></div>";
  }
  alvo.innerHTML=h;
  document.getElementById("vazio").style.display = n? "none":"block";
  var bs=alvo.querySelectorAll("[data-copiar]");
  for(var k=0;k<bs.length;k++) bs[k].onclick=function(){ copiar(this.getAttribute("data-copiar"), this); };
}

document.getElementById("busca").oninput=function(){ filtro=this.value; desenha(); };
desenhaChips(); desenha();
</script>
</body>
</html>
"""


def main():
    itens = le_catalogo()
    if itens is None:
        return 2
    if not itens:
        print(u"NAO MEDI: o catalogo nao tem nenhuma linha de atividade.")
        return 2
    itens.sort(key=lambda a: (a["pos"], a["nome"].lower()))
    import datetime
    # ⚠️ nada de `%` de formatação aqui: o CSS da página tem `width:100%}` e o
    #    format do Python estoura em cima dele. Marcas explícitas, sem surpresa.
    html = (PAGINA
            .replace("@@DADOS@@", json.dumps(itens, ensure_ascii=False))
            .replace("@@TOTAL@@", str(len(itens)))
            .replace("@@QUANDO@@", datetime.date.today().strftime("%d/%m/%Y")))
    io.open(SAIDA, "w", encoding="utf-8").write(html)
    comlink = len([a for a in itens if a["link"]])
    print(u"painel escrito: %s" % SAIDA)
    print(u"   %d atividade(s) em %d turma(s); %d com link, %d sem"
          % (len(itens), len(set(a["turma"] for a in itens)), comlink,
             len(itens) - comlink))
    for a in itens:
        if not a["link"]:
            print(u"   sem link ainda: %s (%s)" % (a["nome"], a["turma"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
