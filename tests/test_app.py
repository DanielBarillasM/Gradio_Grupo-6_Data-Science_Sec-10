import os
import unittest

from app import (
    CATEGORIAS,
    CANALES,
    DATOS,
    REGIONES,
    actualizar_dashboard,
    exportar_csv,
    filtrar_datos,
)


class DashboardTests(unittest.TestCase):
    def test_dataset_tiene_cobertura_completa(self):
        self.assertEqual(len(DATOS), 576)
        self.assertEqual(DATOS["Mes_n"].nunique(), 12)
        self.assertEqual(DATOS["Región"].nunique(), 4)

    def test_filtros_segmentan_region_categoria_canal_y_periodo(self):
        datos = filtrar_datos(["Centro"], ["Tecnología"], ["Web"], [3, 5])
        self.assertEqual(len(datos), 3)
        self.assertEqual(set(datos["Región"]), {"Centro"})
        self.assertEqual(set(datos["Categoría"]), {"Tecnología"})
        self.assertEqual(set(datos["Canal"]), {"Web"})
        self.assertEqual(set(datos["Mes_n"]), {3, 4, 5})

    def test_dashboard_devuelve_ocho_salidas_coordinadas(self):
        salidas = actualizar_dashboard(REGIONES, CATEGORIAS, CANALES, 1, 12, 95_000, "Ventas", "Línea")
        self.assertEqual(len(salidas), 8)
        self.assertIn("576 observaciones", salidas[0])
        self.assertIn("Ventas netas", salidas[1])
        self.assertEqual(len(salidas[-1]), 576)

    def test_exportacion_crea_csv_filtrado(self):
        ruta = exportar_csv(["Sur"], ["Hogar"], ["Tienda"], 1, 2)
        try:
            self.assertTrue(os.path.exists(ruta))
            with open(ruta, encoding="utf-8-sig") as archivo:
                lineas = archivo.readlines()
            self.assertEqual(len(lineas), 3)
        finally:
            if os.path.exists(ruta):
                os.unlink(ruta)


if __name__ == "__main__":
    unittest.main()
