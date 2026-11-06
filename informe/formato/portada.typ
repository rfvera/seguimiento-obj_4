// ========================================
//   PORTADA — SEGUIMIENTO CTD IFOP, OBJETIVO 4
// ========================================

#place(top + left, dx: 1.5cm, dy: 3cm, [
  #rect(
    width: 12cm,
    height: auto,
    fill: none,
    stroke: none,
    inset: 0pt,
    [
      #set text(fill: white)
      #text(size: 25pt, weight: "bold")[INFORME TÉCNICO] \
      #text(size: 16pt, weight: "bold")[Seguimiento CTD — Objetivo 4] \
      #v(1cm)
      #set par(leading: 1.8em)
      #text(size: 14pt, weight: "bold", fill: white)[
        Estado ambiental de referencia y trayectorias de cambio ambiental
        regional en áreas de emplazamiento acuícola, 2019–2025
      ] \
      #v(1cm)
      #text(size: 12pt, fill: white)[Subsecretaría de Pesca y Acuicultura (SUBPESCA)] \
      #text(size: 12pt, fill: white)[Instituto de Fomento Pesquero (IFOP)] \
      #text(size: 12pt, fill: white)[Valparaíso, Chile — 2026.]
    ],
  )
])

#place(top + right, dx: -3cm, dy: 5cm, [
  #text(size: 22pt, weight: "bold", fill: black)[2026]
])

// Logo IFOP en la esquina inferior izquierda
#place(bottom + left, dx: 2cm, dy: -4cm, [
  #image("../imagenes/logo_ifop_2.png", width: 4cm)
])
