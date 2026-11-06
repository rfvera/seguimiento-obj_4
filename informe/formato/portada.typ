// ========================================
//   PORTADA — SEGUIMIENTO CTD IFOP, OBJETIVO 4
// ========================================

#place(top + left, dx: 2cm, dy: 3cm, [
  #rect(
    width: 16cm,
    height: auto,
    fill: none,
    stroke: none,
    inset: 0pt,
    [
      #set text(fill: black)
      #text(size: 28pt, weight: "bold")[INFORME TÉCNICO] \
      #text(size: 16pt, weight: "bold")[Seguimiento CTD — Objetivo 4] \
      #v(1cm)
      #set par(leading: 1.8em)
      #text(size: 14pt, weight: "bold")[
        Estado ambiental de referencia y trayectorias de cambio ambiental
        regional en áreas de emplazamiento acuícola, 2019–2025
      ] \
      #v(1cm)
      #text(size: 12pt)[Subsecretaría de Pesca y Acuicultura (SUBPESCA)] \
      #text(size: 12pt)[Instituto de Fomento Pesquero (IFOP)] \
      #v(0.5cm)
      #text(size: 11pt)[Valparaíso, Chile — 2026]
    ],
  )
])

// Logo IFOP en la esquina inferior izquierda
#place(bottom + left, dx: 2cm, dy: -3cm, [
  #image("../imagenes/logo_ifop_2.png", width: 4cm)
])
