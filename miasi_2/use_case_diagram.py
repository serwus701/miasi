import xml.etree.ElementTree as ET
import svgwrite


def parse_xml_to_svg(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    dwg = svgwrite.Drawing(filename=output_file, profile='full')

    # Get UseCase elements
    use_cases = root.findall('.//UseCaseDiagram/Shapes/UseCase')

    # Draw use cases as ellipses
    for use_case in use_cases:
        x = int(use_case.attrib['X'])
        y = int(use_case.attrib['Y'])
        width = int(use_case.attrib['Width'])
        height = int(use_case.attrib['Height'])
        name = use_case.attrib['Name']

        dwg.add(dwg.ellipse(center=(x + width / 2, y + height / 2), r=(width / 2, height / 2), fill='lightblue',
                            stroke='black'))
        dwg.add(
            dwg.text(name, insert=(x + width / 2, y + height / 2), text_anchor="middle", alignment_baseline="middle",
                     font_size=12, font_family='Dialog'))

    # Get Associations
    associations = root.findall('.//UseCaseDiagram/Connectors/Association')

    # Draw associations
    for association in associations:
        points = [(float(point.attrib['X']), float(point.attrib['Y'])) for point in
                  association.findall('.//Points/Point')]
        dwg.add(dwg.polyline(points, stroke='black', fill='none', stroke_width=1))

    dwg.save()


# Use the function
parse_xml_to_svg('usecase_diagram.xml', 'usecase_diagram.svg')
