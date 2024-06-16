from lxml import etree
import svgwrite
import math


def parse_uml_xml(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    return root


def map_uml_to_svg(uml_root):
    actors = uml_root.findall('.//actor')
    usecases = uml_root.findall('.//usecase')
    associations = uml_root.findall('.//association')
    return actors, usecases, associations


def calculate_positions(elements, canvas_size, column, inheritance_map, x_offset=0, y_offset=0):
    y_step = canvas_size[1] / (len(elements) + 1)
    x_pos = column * canvas_size[0] / 4 + x_offset
    positions = {}

    for idx, elem in enumerate(elements):
        y_pos = (idx + 1) * y_step + y_offset
        positions[elem.get('name')] = (x_pos, y_pos)

    return positions


def draw_actor(dwg, center):
    head_radius = 10
    body_height = 40
    arm_length = 20
    leg_length = 20

    head_center = (center[0], center[1] - body_height // 2 - head_radius)
    body_start = (center[0], head_center[1] + head_radius)
    body_end = (center[0], body_start[1] + body_height)
    left_arm_end = (center[0] - arm_length, body_start[1] + arm_length)
    right_arm_end = (center[0] + arm_length, body_start[1] + arm_length)
    left_leg_end = (center[0] - leg_length, body_end[1] + leg_length)
    right_leg_end = (center[0] + leg_length, body_end[1] + leg_length)

    dwg.add(dwg.circle(center=head_center, r=head_radius, fill='blue', stroke='black'))
    dwg.add(dwg.line(start=body_start, end=body_end, stroke='black'))
    dwg.add(dwg.line(start=body_start, end=left_arm_end, stroke='black'))
    dwg.add(dwg.line(start=body_start, end=right_arm_end, stroke='black'))
    dwg.add(dwg.line(start=body_end, end=left_leg_end, stroke='black'))
    dwg.add(dwg.line(start=body_end, end=right_leg_end, stroke='black'))
    return body_start, body_end


def generate_svg(actors, usecases, associations, output_file):
    canvas_size = (1600, 1200)
    dwg = svgwrite.Drawing(output_file, profile='full', size=canvas_size)

    inheritance_map = {assoc.get('to'): assoc.get('from') for assoc in associations if
                       assoc.get('type') == 'inheritance'}
    other_associations = [assoc for assoc in associations if assoc.get('type') != 'inheritance']

    left_actors = [actor for actor in actors if
                   actor.get('name') in inheritance_map.values() or actor.get('name') in inheritance_map]
    right_actors = [actor for actor in actors if actor not in left_actors]

    left_actor_positions = calculate_positions(left_actors, canvas_size, 0, inheritance_map, x_offset=100)
    right_actor_positions = calculate_positions(right_actors, canvas_size, 3, inheritance_map, x_offset=-100)
    usecase_positions = calculate_positions(usecases, canvas_size, 1.5, {}, x_offset=0)

    # Merge positions
    actor_positions = {**left_actor_positions, **right_actor_positions}

    # Adjust usecase positions if only one actor uses them
    usecase_actor_map = {uc.get('name'): [] for uc in usecases}
    for assoc in other_associations:
        from_elem = assoc.get('from')
        to_elem = assoc.get('to')
        if from_elem in actor_positions:
            usecase_actor_map[to_elem].append(from_elem)
        elif to_elem in actor_positions:
            usecase_actor_map[from_elem].append(to_elem)

    for usecase in usecases:
        usecase_name = usecase.get('name')
        if len(usecase_actor_map[usecase_name]) == 1:
            actor_name = usecase_actor_map[usecase_name][0]
            actor_x, actor_y = actor_positions[actor_name]
            usecase_positions[usecase_name] = (
            actor_x + 300 if actor_x < canvas_size[0] // 2 else actor_x - 300, actor_y)

    # Draw actors
    body_points = {}
    for actor in actors:
        actor_name = actor.get('name')
        actor_x, actor_y = actor_positions[actor_name]

        body_start, body_end = draw_actor(dwg, (actor_x, actor_y))
        body_points[actor_name] = (body_start, body_end)
        dwg.add(dwg.text(actor_name, insert=(actor_x, actor_y + 60), fill='black', text_anchor="middle"))

    # Draw usecases
    for usecase in usecases:
        usecase_name = usecase.get('name')
        usecase_x, usecase_y = usecase_positions[usecase_name]

        dwg.add(dwg.ellipse(center=(usecase_x, usecase_y), r=(60, 30), fill='white', stroke='black'))
        dwg.add(dwg.text(usecase_name, insert=(usecase_x, usecase_y + 5), fill='black', text_anchor="middle"))

    # Draw associations
    def adjust_to_border(start, end, ellipse_pos, ellipse_size):
        px, py = start
        ex, ey = end
        ex, ey = ellipse_pos
        ew, eh = ellipse_size

        dx, dy = px - ex, py - ey
        if dx == 0:
            if dy > 0:
                return (ex, ey + eh)
            else:
                return (ex, ey - eh)
        if dy == 0:
            if dx > 0:
                return (ex + ew, ey)
            else:
                return (ex - ew, ey)

        slope = dy / dx
        if abs(slope) < eh / ew:
            if dx > 0:
                return (ex + ew, ey + eh * slope)
            else:
                return (ex - ew, ey - eh * slope)
        else:
            if dy > 0:
                return (ex + ew / slope, ey + eh)
            else:
                return (ex - ew / slope, ey - eh)

    def draw_curved_line(dwg, start, end, dashed=False):
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        path = dwg.path(d=f"M {start[0]},{start[1]} Q {mid_x},{mid_y - 50} {end[0]},{end[1]}", stroke='black',
                        fill='none')
        if dashed:
            path.dasharray([5, 5])
        return path

    for assoc in associations:
        from_elem = assoc.get('from')
        to_elem = assoc.get('to')
        assoc_type = assoc.get('type', 'association')

        if from_elem in actor_positions and to_elem in usecase_positions:
            from_pos = actor_positions[from_elem]
            to_pos = usecase_positions[to_elem]
        elif from_elem in usecase_positions and to_elem in actor_positions:
            from_pos = usecase_positions[from_elem]
            to_pos = actor_positions[to_elem]
        elif from_elem in actor_positions and to_elem in actor_positions:
            from_pos = actor_positions[from_elem]
            to_pos = actor_positions[to_elem]
        else:
            continue

        from_body_start, from_body_end = body_points.get(from_elem, ((0, 0), (0, 0)))
        from_center = ((from_body_start[0] + from_body_end[0]) / 2, (from_body_start[1] + from_body_end[1]) / 2)

        from_border = adjust_to_border(from_center, to_pos, from_center, (10, 20))
        to_border = adjust_to_border(to_pos, from_center, to_pos, (60, 30))

        path = draw_curved_line(dwg, from_border, to_border, dashed=(assoc_type == 'association'))

        dwg.add(path)

        arrow_size = 10
        if assoc_type == 'aggregation':
            dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + arrow_size, to_border[1]),
                                        (to_border[0], to_border[1] + 5), (to_border[0] - arrow_size, to_border[1])],
                                fill='white', stroke='black'))
        elif assoc_type == 'composition':
            dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + arrow_size, to_border[1]),
                                        (to_border[0], to_border[1] + 5), (to_border[0] - arrow_size, to_border[1])],
                                fill='black'))
        elif assoc_type == 'inheritance':
            dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + arrow_size, to_border[1]),
                                        (to_border[0], to_border[1] + 5)], fill='white', stroke='black'))
        elif assoc_type == 'implementation':
            dwg.add(dwg.polygon(points=[(to_border[0], to_border[1] - 5), (to_border[0] + arrow_size, to_border[1]),
                                        (to_border[0], to_border[1] + 5)], fill='white', stroke='black'))

    dwg.save()


def main():
    xml_file = 'usecase_diagram.xml'
    output_file = 'usecase_diagram.svg'

    uml_root = parse_uml_xml(xml_file)
    actors, usecases, associations = map_uml_to_svg(uml_root)
    generate_svg(actors, usecases, associations, output_file)


if __name__ == "__main__":
    main()
