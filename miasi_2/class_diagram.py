from lxml import etree
import svgwrite
import math


def parse_uml_xml(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    return root


def map_uml_to_svg(uml_root):
    classes = uml_root.findall('.//class')
    associations = uml_root.findall('.//association')
    return classes, associations


def calculate_class_positions(classes, class_size, canvas_size):
    radius = min(canvas_size) // 2 - class_size[0]
    angle_step = 2 * math.pi / len(classes)
    center = (canvas_size[0] // 2, canvas_size[1] // 2)

    class_positions = {}
    for idx, cls in enumerate(classes):
        angle = idx * angle_step
        class_x = center[0] + radius * math.cos(angle) - class_size[0] // 2
        class_y = center[1] + radius * math.sin(angle) - class_size[1] // 2
        class_positions[cls.get('name')] = (class_x, class_y)

    return class_positions


def generate_svg(classes, associations, output_file):
    canvas_size = (1200, 1200)
    class_size = (200, 150)
    dwg = svgwrite.Drawing(output_file, profile='full', size=canvas_size)

    class_positions = calculate_class_positions(classes, class_size, canvas_size)

    # Draw classes
    for cls in classes:
        class_name = cls.get('name')
        class_type = cls.get('type')
        class_x, class_y = class_positions[class_name]

        if class_type == 'class':
            dwg.add(dwg.rect(insert=(class_x, class_y), size=class_size, fill='white', stroke='black'))
        elif class_type == 'abstract':
            dwg.add(dwg.rect(insert=(class_x, class_y), size=class_size, fill='white', stroke='black',
                             stroke_dasharray="5,5"))
        elif class_type == 'interface':
            dwg.add(dwg.rect(insert=(class_x, class_y), size=class_size, fill='lightblue', stroke='black'))

        dwg.add(dwg.text(f"Class: {class_name}", insert=(class_x + 10, class_y + 20), fill='black'))

        dwg.add(dwg.line(start=(class_x, class_y + 30), end=(class_x + class_size[0], class_y + 30), stroke='black'))

        attr_y = class_y + 40
        for attr in cls.findall('.//attribute'):
            attr_name = attr.get('name')
            attr_type = attr.get('type')
            visibility = attr.get('visibility')
            visibility_symbol = {'public': '+', 'protected': '#', 'private': '-'}[visibility]
            dwg.add(
                dwg.text(f'{visibility_symbol} {attr_name}: {attr_type}', insert=(class_x + 10, attr_y), fill='black'))
            attr_y += 20

        dwg.add(dwg.line(start=(class_x, attr_y - 10), end=(class_x + class_size[0], attr_y - 10), stroke='black',
                         stroke_dasharray="5,5"))

        for method in cls.findall('.//method'):
            method_name = method.get('name')
            return_type = method.get('return')
            visibility = method.get('visibility')
            visibility_symbol = {'public': '+', 'protected': '#', 'private': '-'}[visibility]
            dwg.add(dwg.text(f'{visibility_symbol} {method_name}(): {return_type}', insert=(class_x + 10, attr_y),
                             fill='blue'))
            attr_y += 20

    # Draw associations
    def adjust_to_border(start, end, rect_pos, rect_size):
        px, py = start
        ex, ey = end
        rx, ry = rect_pos
        rw, rh = rect_size

        if px == ex:
            if py < ey:
                return (px, ry + rh)
            else:
                return (px, ry)

        if py == ey:
            if px < ex:
                return (rx + rw, py)
            else:
                return (rx, py)

        slope = (ey - py) / (ex - px)
        if ex > px:
            border_x = rx + rw
            border_y = py + slope * (border_x - px)
            if ry <= border_y <= ry + rh:
                return (border_x, border_y)
        if ex < px:
            border_x = rx
            border_y = py + slope * (border_x - px)
            if ry <= border_y <= ry + rh:
                return (border_x, border_y)
        if ey > py:
            border_y = ry + rh
            border_x = px + (border_y - py) / slope
            if rx <= border_x <= rx + rw:
                return (border_x, border_y)
        if ey < py:
            border_y = ry
            border_x = px + (border_y - py) / slope
            if rx <= border_x <= rx + rw:
                return (border_x, border_y)

        return (px, py)

    def draw_curved_line(dwg, start, end):
        path = dwg.path(
            d="M {},{} Q {},{} {},{}".format(start[0], start[1], (start[0] + end[0]) / 2, (start[1] + end[1]) / 2 - 50,
                                             end[0], end[1]), stroke='black', fill='none')
        return path

    for assoc in associations:
        from_class = assoc.get('from')
        to_class = assoc.get('to')
        assoc_type = assoc.get('type', 'association')

        if from_class in class_positions and to_class in class_positions:
            from_pos = class_positions[from_class]
            to_pos = class_positions[to_class]

            from_center = (from_pos[0] + class_size[0] // 2, from_pos[1] + class_size[1] // 2)
            to_center = (to_pos[0] + class_size[0] // 2, to_pos[1] + class_size[1] // 2)

            from_border = adjust_to_border(from_center, to_center, from_pos, class_size)
            to_border = adjust_to_border(to_center, from_center, to_pos, class_size)

            path = draw_curved_line(dwg, from_border, to_border)

            if assoc_type == 'association':
                dwg.add(path)
            elif assoc_type == 'aggregation':
                dwg.add(path)
                dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + 10, to_border[1]),
                                            (to_border[0], to_border[1] + 5), (to_border[0] - 10, to_border[1])],
                                    fill='white', stroke='black'))
            elif assoc_type == 'composition':
                dwg.add(path)
                dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + 10, to_border[1]),
                                            (to_border[0], to_border[1] + 5), (to_border[0] - 10, to_border[1])],
                                    fill='black'))
            elif assoc_type == 'inheritance':
                dwg.add(path)
                dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + 10, to_border[1]),
                                            (to_border[0], to_border[1] + 5)], fill='white', stroke='black'))
            elif assoc_type == 'implementation':
                path.dasharray([5, 5])  # Dashed line for interface implementation
                dwg.add(path)
                dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + 10, to_border[1]),
                                            (to_border[0], to_border[1] + 5)], fill='white', stroke='black'))

    dwg.save()


def main():
    xml_file = 'class_diagram.xml'
    output_file = 'class_diagram.svg'

    uml_root = parse_uml_xml(xml_file)
    classes, associations = map_uml_to_svg(uml_root)
    generate_svg(classes, associations, output_file)


if __name__ == "__main__":
    main()
