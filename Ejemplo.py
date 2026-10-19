import gradio as gr


def saludar(nombre, intensidad):
    return f"Hola, {nombre}" + "!" * int(intensidad)


demo = gr.Interface(
    fn=saludar,
    inputs=[gr.Textbox(label="Nombre"), gr.Slider(1, 5, step=1)],
    outputs=gr.Textbox(label="Resultado"),
)

if __name__ == "__main__":
    demo.launch()
