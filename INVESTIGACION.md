# Investigación: dashboards interactivos con énfasis en Gradio

**CC3084 · Data Science · Sección 10 · Grupo 6**<br>
**Universidad del Valle de Guatemala · Segundo semestre de 2026**<br>
Pablo Daniel Barillas Moreno — Carné No. 222193<br>
Carlos Aldana — Carné No. 23394<br>
Fecha de consulta: 19 de octubre de 2026.

## 1. Definición y propósito

Un dashboard interactivo es una aplicación visual que combina indicadores, tablas y gráficas con controles que permiten explorar la información. Su valor no está en acumular elementos visuales, sino en facilitar un ciclo de decisión: **observar → preguntar → comparar → actuar**.

Gradio es un paquete open source de Python para convertir funciones, modelos y flujos de datos en aplicaciones web. Una primera interfaz puede construirse sin JavaScript ni configuración manual de un servidor; la API `Blocks` permite después controlar distribución, eventos y salidas coordinadas. El proyecto se publica con licencia Apache 2.0.

## 2. Panorama de herramientas

| Herramienta | Lenguajes | Enfoque | Cuándo destaca |
|---|---|---|---|
| **Gradio** | Python; clientes Python y JS/TS | Interfaces para funciones, IA, multimedia y APIs | Demos, prototipos, docencia y herramientas internas |
| **Streamlit** | Python | Aplicaciones de datos con modelo de reejecución | Exploración rápida y narrativas de datos |
| **Dash** | Python | Callbacks explícitos y visualizaciones Plotly | Aplicaciones analíticas estructuradas |
| **Panel** | Python | Integración con PyData, HoloViz y notebooks | Ecosistemas científicos heterogéneos |
| **Shiny** | R y Python | Programación reactiva | Equipos estadísticos y aplicaciones modulares |

La elección no debe depender solo de la facilidad del primer ejemplo. También deben evaluarse control visual, tipo de interacción, autenticación, carga esperada, costos de operación, habilidades del equipo y plataforma de despliegue.

## 3. Lenguajes y ecosistema de Gradio

- **Python**: autoría de la interfaz, lógica, datos, modelos y eventos.
- **JavaScript/TypeScript**: `@gradio/client` consume una aplicación como endpoint.
- **Python client**: `gradio_client` permite invocaciones programáticas.
- **Ecosistema web**: una app puede funcionar simultáneamente como interfaz humana y API.
- **Hugging Face Spaces**: alojamiento versionado para demostraciones y proyectos públicos o privados, según la configuración de la cuenta.

### Niveles de abstracción

- `gr.Interface`: envuelve una función con entradas y salidas declarativas.
- `gr.Blocks`: organiza componentes, pestañas, filas, columnas, eventos y estado.
- `gr.ChatInterface`: ofrece el patrón conversacional con historial y streaming.

## 4. Desarrollo básico

```python
import gradio as gr

def saludar(nombre, intensidad):
    return f"Hola, {nombre}" + "!" * int(intensidad)

demo = gr.Interface(
    fn=saludar,
    inputs=[gr.Textbox(label="Nombre"), gr.Slider(1, 5, step=1)],
    outputs=gr.Textbox(label="Resultado"),
)

demo.launch()
```

El patrón consta de cuatro pasos: escribir una función, declarar los componentes, conectarlos y lanzar el servidor. En una aplicación mayor, un evento como `boton.click(fn=analizar, inputs=[...], outputs=[...])` actualiza varias salidas con una sola ejecución.

## 5. Estado, eventos y concurrencia

Gradio distingue datos globales, estado de sesión (`gr.State`) y preferencias persistentes del navegador (`gr.BrowserState`). Un estado global mutable puede filtrar datos entre usuarios; para información privada debe usarse un alcance aislado.

Cada listener puede usar una cola. `concurrency_limit` limita cuántas ejecuciones simultáneas se aceptan, lo cual es importante para modelos con GPU, tareas largas o APIs con cuota. Aumentar concurrencia sin medir memoria y latencia no garantiza mayor rendimiento.

La aplicación del grupo utiliza eventos coordinados, contrato fijo de ocho salidas, límite de cuatro ejecuciones concurrentes y exportación explícita de resultados.

## 6. Observatorio comercial del grupo

El archivo `app.py` implementa un caso reproducible con 576 registros sintéticos de 2026:

- cuatro regiones: Centro, Norte, Sur y Occidente;
- cuatro categorías: Tecnología, Hogar, Oficina y Accesorios;
- tres canales: Tienda, Web y Distribuidores;
- 12 meses, ventas, costos, unidades, pedidos y satisfacción;
- filtros múltiples, rango temporal y meta mensual configurable;
- métricas de ventas o unidades y vistas de línea, barras o área;
- cinco KPIs y cuatro visualizaciones complementarias;
- interpretación automática, tabla y descarga CSV.

Los cálculos centrales son:

```text
Margen bruto % = Σ(Ventas − Costo) / Σ(Ventas) × 100
Ticket promedio = ΣVentas / ΣPedidos
Cumplimiento % = promedio mensual / meta ajustada × 100
Crecimiento % = (último mes / primer mes − 1) × 100
```

La meta se ajusta proporcionalmente al número de categorías y canales seleccionados para mantener una comparación interpretable después de segmentar.

## 7. Calidad, diseño y accesibilidad

La solución usa un contenedor central con ancho máximo, columnas que pueden contraerse (`min-width: 0`) y puntos de quiebre para evitar el recorte que aparecía en la versión inicial. La jerarquía visual separa contexto, filtros, KPIs, análisis y detalle; el violeta identifica acciones o estados seleccionados y el naranja representa metas.

Se validaron cuatro pruebas automáticas:

1. cobertura exacta de 576 observaciones;
2. filtrado por dimensiones y meses;
3. contrato de ocho salidas coordinadas;
4. creación de un CSV filtrado.

También se revisó la aplicación en un navegador real a 1920 × 1080, se recorrieron pestañas y cambios de métrica, y se comprobó la consola sin errores ni advertencias.

## 8. Seguridad, privacidad y producción

Antes de publicar una aplicación se recomienda:

- permitir solo los archivos estrictamente necesarios y validar cargas;
- mantener secretos fuera del repositorio y del frontend;
- usar autenticación y HTTPS en infraestructura propia;
- limitar tamaño de archivos, concurrencia, tiempo y memoria;
- evitar datos sensibles en enlaces públicos temporales;
- registrar latencia, errores, saturación de cola y consumo de recursos;
- mantener Gradio y sus dependencias actualizados.

`share=True` crea una demostración pública temporal que sigue dependiendo del proceso local. Para una publicación persistente puede utilizarse Hugging Face Spaces, un contenedor propio o una plataforma administrada.

## 9. Sitio, referencias y comunidad

- [Sitio oficial](https://www.gradio.app/)
- [Quickstart](https://www.gradio.app/guides/quickstart)
- [Documentación de Blocks](https://www.gradio.app/docs/gradio/blocks)
- [Guía de colas](https://www.gradio.app/guides/queuing)
- [Estado en Blocks](https://www.gradio.app/main/guides/state-in-blocks)
- [Temas](https://www.gradio.app/guides/theming-guide)
- [CSS y JavaScript personalizados](https://www.gradio.app/guides/custom-CSS-and-JS)
- [Seguridad y acceso a archivos](https://www.gradio.app/guides/file-access)
- [Repositorio e issues](https://github.com/gradio-app/gradio)
- [Discord oficial](https://discord.gg/feTf9x3ZSB)
- [Ejemplos del equipo Gradio](https://huggingface.co/gradio/spaces)
- [Artículo original: *Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild*](https://arxiv.org/abs/1906.02569)

## 10. Guion sugerido para la exposición (8–10 minutos)

1. **Problema:** transformar análisis o modelos de Python en experiencias utilizables.
2. **Panorama:** comparar Gradio, Streamlit, Dash, Panel y Shiny.
3. **Concepto:** explicar función, componentes, evento y resultados.
4. **Hello World:** mostrar `gr.Interface` y las cuatro etapas del desarrollo.
5. **Demo:** filtrar segmentos, cambiar métrica y recorrer las tres pestañas.
6. **Arquitectura:** navegador → componentes → evento/cola → función Python → resultados.
7. **Ingeniería:** estado, concurrencia, seguridad, pruebas y despliegue.
8. **Conclusión:** Gradio reduce el tiempo hasta una interfaz útil; producción exige decisiones adicionales de operación y seguridad.

## 11. Conclusión

Gradio es una opción especialmente eficaz cuando el núcleo ya existe en Python y se necesita una interfaz demostrable con rapidez. El observatorio desarrollado prueba que también puede sostener un dashboard analítico de complejidad media, siempre que la lógica, el estado, la composición visual y las pruebas se diseñen explícitamente. Para productos empresariales con navegación extensa, identidad visual estricta o control avanzado de acceso, debe compararse con frameworks analíticos o una aplicación web a medida.
