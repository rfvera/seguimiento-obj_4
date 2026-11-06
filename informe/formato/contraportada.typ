// ================== CONTRAPORTADA ==================
// Esta página usa su propia configuración, sin afectar al resto del documento
#page(
  paper: "a4",
  margin: 0cm,
  header: none,
  footer: none,
  background: image("../imagenes/portada.png", width: 100%, height: 100%, fit: "cover")
)[
  #align(center + horizon)[
    #text(size: 16pt, fill: white, weight: "bold")[SEGUIMIENTO CTD IFOP — OBJETIVO 4]
    #v(0.5cm)
    #text(size: 12pt, fill: white)[Estado ambiental de referencia y trayectorias de cambio ambiental regional, 2019–2025]
    #v(2cm)
    #image("../imagenes/logo_ifop_2.png", width: 4cm)
    #v(1cm)
    #text(size: 10pt, fill: white)[Instituto de Fomento Pesquero (IFOP) \
    Blanco 839, Valparaíso, Chile \
    www.ifop.cl]
  ]
]
