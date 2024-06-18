import xml.etree.ElementTree as ET
import svgwrite
import math

def arrowhead_coordinates(x1, y1, x2, y2):
    arrow_length = 10
    arrow_angle_degrees = 45
    theta = math.atan2(y2 - y1, x2 - x1)

    alpha = math.radians(arrow_angle_degrees)

    x3 = x2 - arrow_length * math.cos(theta - alpha)
    y3 = y2 - arrow_length * math.sin(theta - alpha)

    x4 = x2 - arrow_length * math.cos(theta + alpha)
    y4 = y2 - arrow_length * math.sin(theta + alpha)

    return (x3, y3), (x4, y4)

def parse_usecase_diagram(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    diagrams = root.find(".//Diagrams")
    system = root.find(".//UseCaseDiagram")
    relations = root.find(".//Models/ModelRelationshipContainer/ModelChildren")

    actors = {}
    use_cases = []
    associations = []
    dependencies = []
    systems = []

    actor_coords = {actor.get('Id'): (actor.get('X'), actor.get('Y'))
                    for actor in root.findall(".//Diagrams/UseCaseDiagram/Shapes/Actor")}

    for actor in diagrams.findall(".//Actor"):
        actor_id = actor.get('Id')
        actor_name = actor.get('Name')
        if actor_id in actor_coords:
            coords = actor_coords[actor_id]
            actors[actor_id] = {'name': actor_name, 'coords': coords}
        else:
            actors[actor_id] = {'name': actor_name, 'coords': (None, None)}

    for use_case in system.findall(".//UseCase"):
        use_cases.append({
            'id': use_case.get('Id'),
            'name': use_case.get('Name'),
            'x': use_case.get('X'),
            'y': use_case.get('Y')
        })

    for association in relations.findall(".//Association"):
        new_association = {"source": "", "destination": ""}
        if association.find('.//FromEnd') is None:
            continue
        from_end = association.find('.//FromEnd')
        use_case = from_end.find('.//UseCase')
        actor = from_end.find('.//Actor')
        if use_case is not None:
            new_association["source"] = use_case.get("Idref")
        elif actor is not None:
            new_association["source"] = actor.get("Idref")

        to_end = association.find('.//ToEnd')
        use_case = to_end.find('.//UseCase')
        actor = to_end.find('.//Actor')
        if use_case is not None:
            new_association["destination"] = use_case.get("Idref")
        elif actor is not None:
            new_association["destination"] = actor.get("Idref")

        associations.append(new_association)

    for dependency in relations.findall(".//Dependency"):
        if dependency.find('.//MasterView') is None:
            continue
        dependencies.append({
            'from': dependency.get("From"),
            'to': dependency.get("To")
        })

    for system in diagrams.findall('.//System'):
        systems.append({
            'id': system.get('Id'),
            'name': system.get('Name'),
            'x': int(system.get('X')),
            'y': int(system.get('Y')),
            'width': int(system.get('Width')),
            'height': int(system.get('Height'))
        })

    return actors, use_cases, associations, dependencies, systems


def draw_usecase_diagram(actors, use_cases, associations, dependencies, systems, svg_file):
    coords_map = {}

    for id, actor in actors.items():
        x, y = map(int, actor['coords'])
        coords_map[id[:-1]] = (x, y)

    for use_case in use_cases:
        coords_map[use_case['id'][:-1]] = (int(use_case['x']), int(use_case['y']))

    dwg = svgwrite.Drawing(svg_file, profile='tiny')

    actor_positions = {}
    use_case_positions = {}

    for system in systems:
        x, y, width, height = system['x'], system['y'], system['width'], system['height']
        dwg.add(dwg.rect(insert=(x, y), size=(width, height), fill='lightblue', stroke='black'))
        dwg.add(dwg.text(system['name'], insert=(x + 10, y + 20), font_size=15, font_weight="bold"))

    for actor_id, actor_details in actors.items():
        x, y = map(int, actor_details['coords'])
        actor_positions[actor_id] = (x, y)
        dwg.add(dwg.circle(center=(x, y - 20), r=10, fill='blue'))  # Głowa
        dwg.add(dwg.line(start=(x, y - 10), end=(x, y + 20), stroke='black'))  # Ciało
        dwg.add(dwg.line(start=(x, y), end=(x - 10, y + 10), stroke='black'))  # Lewa ręka
        dwg.add(dwg.line(start=(x, y), end=(x + 10, y + 10), stroke='black'))  # Prawa ręka
        dwg.add(dwg.line(start=(x, y + 20), end=(x - 10, y + 30), stroke='black'))  # Lewa noga
        dwg.add(dwg.line(start=(x, y + 20), end=(x + 10, y + 30), stroke='black'))  # Prawa noga
        dwg.add(dwg.text(actor_details["name"], insert=(int(x) - 20, int(y) - 30)))

    for use_case in use_cases:
        x, y = map(int, (use_case['x'], use_case['y']))
        use_case_positions[use_case['id']] = (x, y)
        dwg.add(dwg.ellipse(center=(x, y), r=(60, 30), fill='#3483eb'))
        dwg.add(dwg.text(use_case['name'], insert=(x-25, y)))

    for association in associations:
        id_source = association['source'][:-1]
        id_destination = association['destination'][:-1]
        line_begin = coords_map[id_source]
        line_end = coords_map[id_destination]
        dwg.add(dwg.line(start=line_begin, end=line_end, stroke=svgwrite.rgb(0, 0, 0, '%')))

    for dependency in dependencies:
        id_source = dependency['from'][:-1]
        id_destination = dependency['to'][:-1]
        line_begin = coords_map[id_source]
        line_end = coords_map[id_destination]
        dwg.add(dwg.line(start=line_begin, end=line_end, stroke=svgwrite.rgb(0, 0, 0, '%'), stroke_dasharray="5,5"))
        (x2, y2),(x1, y1) =arrowhead_coordinates(*line_begin, *line_end )
        dwg.add(dwg.line(start=(x1, y1), end=line_end, stroke=svgwrite.rgb(0, 0, 0, '%')))
        dwg.add(dwg.line(start=(x2, y2), end=line_end, stroke=svgwrite.rgb(0, 0, 0, '%')))

    dwg.save()


xml_file = 'usecase_diagram.xml'
svg_file = 'usecase_diagram.svg'

actors, use_cases, associations, dependencies, systems = parse_usecase_diagram(xml_file)
draw_usecase_diagram(actors, use_cases, associations, dependencies, systems, svg_file)

print(f'Diagram zapisany w {svg_file}')
