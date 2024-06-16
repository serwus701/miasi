import xml.etree.ElementTree as ET
import svgwrite


def parse_activity_diagram(xml_file):
    # Parsowanie pliku XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Inicjalizacja SVG
    dwg = svgwrite.Drawing(filename="output.svg", size=("100%", "100%"))

    # Definicje stylów SVG
    dwg.defs.add(dwg.style(".activity { fill: #f0f0f0; stroke: #333; stroke-width: 2px; }"))
    dwg.defs.add(dwg.style(".transition { stroke: #333; stroke-width: 2px; }"))
    dwg.defs.add(dwg.style(".text { font-family: Arial, sans-serif; font-size: 14px; }"))

    # Słownik do przechowywania kształtów (Shapes)
    shapes_dict = {}

    # Przechodzenie przez kształty (Shapes)
    for shape in root.findall(".//Shape"):
        shape_id = shape.get("id")
        shape_name = shape.get("name")
        shape_type = shape.get("shapeType")
        x = int(shape.get("x"))
        y = int(shape.get("y"))
        width = int(shape.get("width"))
        height = int(shape.get("height"))

        # Tworzenie prostokąta reprezentującego kształt (Shape)
        shape_rect = dwg.rect(insert=(x, y), size=(width, height), class_="activity")
        shape_label = dwg.text(shape_name, insert=(x + 10, y + 20), class_="text")

        # Dodawanie kształtu do SVG i do słownika
        dwg.add(shape_rect)
        dwg.add(shape_label)
        shapes_dict[shape_id] = {"rect": shape_rect, "x": x, "y": y, "width": width,
                                 "height": height}  # Dodajemy kształt do słownika

    # Przechodzenie przez połączenia (Connectors)
    for connector in root.findall(".//Connector"):
        connector_id = connector.get("id")
        from_id = connector.get("from")
        to_id = connector.get("to")

        # Wyszukiwanie kształtów w słowniku
        if from_id in shapes_dict and to_id in shapes_dict:
            from_shape = shapes_dict[from_id]
            to_shape = shapes_dict[to_id]

            # Punkty połączenia
            from_x = from_shape["x"] + from_shape["width"]  # Prawa krawędź
            from_y = from_shape["y"] + from_shape["height"] / 2  # Środek wysokości

            to_x = to_shape["x"]  # Lewa krawędź
            to_y = to_shape["y"] + to_shape["height"] / 2  # Środek wysokości

            # Jeśli from_x > to_x, ustaw punkty w inny sposób, aby linie były krótsze
            if from_x > to_x:
                from_x = from_shape["x"]  # Lewa krawędź
                to_x = to_shape["x"] + to_shape["width"]  # Prawa krawędź

            # Tworzenie linii reprezentującej połączenie (Connector)
            transition_line = dwg.line(start=(from_x, from_y), end=(to_x, to_y), class_="transition")

            # Dodawanie połączenia do SVG
            dwg.add(transition_line)

    # Zapis SVG do pliku
    dwg.save()

if __name__ == "__main__":
    xml_file = "sumxmls/traditional_activity_simple.xml"  # Nazwa pliku XML z diagramem aktywności
    parse_activity_diagram(xml_file)
