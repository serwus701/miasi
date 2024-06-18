import math
import xml.etree.ElementTree as ET
import svgwrite

def parse_caption_pos(elem):
    for child in elem:
        if child.tag.endswith('Caption'):
            x = int(child.attrib.get('X'))
            y = int(child.attrib.get('Y'))
            height = int(elem.attrib.get('Height', 0))
            width = int(elem.attrib.get('Width', 0))
            return {'height':height, 'width':width, 'x': x, 'y': y}
    return {'x': 0, 'y': 0}

def wrap_text_by_approx_width(text, max_width, font_size):
    """
    Wrap text into lines that fit within the given max_width in pixels.
    This function uses an approximate method to calculate text width based on character count.

    text: The text to wrap.
    max_width: The maximum width of each line in pixels.
    font_size: Font size in points.
    """
    avg_char_width = font_size * 0.6
    max_chars_per_line = max_width // avg_char_width

    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word) * avg_char_width

        while word_length > max_chars_per_line * avg_char_width:
            split_index = int(max_chars_per_line)
            current_line.append(word[:split_index])
            lines.append(" ".join(current_line))
            word = word[split_index:]
            word_length = len(word) * avg_char_width
            current_line = []
            current_length = 0

        if current_length + word_length + (avg_char_width if current_line else 0) <= max_width:
            current_line.append(word)
            current_length += word_length + (avg_char_width if current_line else 0)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def parse_xml_to_svg(xml_file, svg_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        diagrams = root.find('Diagrams')
        dwg = svgwrite.Drawing(svg_file, profile='full')

        swimlane_style = {'stroke': 'black', 'fill': 'none', 'stroke-width': 2}
        activity_swimlane2_style = {'stroke': 'black', 'fill': 'none', 'stroke-width': 2}
        activity_style = {'stroke': 'black', 'fill': 'rgb(122, 207, 245)', 'stroke-width': 1, 'rx': 10, 'ry': 10}
        decision_node_style = {'stroke': 'black', 'fill': 'rgb(122, 207, 245)', 'stroke-width': 1}
        connector_style = {'stroke': 'black', 'stroke-width': 1}

        element_positions = {}

        swimlanes_count = 0
        # Find and place ActivitySwimlane2
        for swimlane in diagrams.findall(".//ActivitySwimlane2"):
            x = float(swimlane.get('X', '0'))
            y = float(swimlane.get('Y', '0'))
            width = float(swimlane.get('Width', '0'))
            height = float(swimlane.get('Height', '0'))

            element_positions[swimlanes_count] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, height), **swimlane_style))

            swimlanes_count += 1
        print(f"Total SwimLanes: {swimlanes_count}")

        partition_headers_count = 0
        # Find and place ActivityPartitionHeader
        for partition_header in diagrams.findall(".//ActivityPartitionHeader"):
            id = partition_header.get('Id')
            x = float(partition_header.get('X', '0'))
            y = float(partition_header.get('Y', '0'))
            width = float(partition_header.get('Width', '200'))
            height = float(partition_header.get('Height', '40'))
            name = partition_header.get('Name')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)

            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }

            background_style = {
                'stroke': 'black',
                'fill': 'white',
                'stroke-width': 2
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, height), **background_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y + 11 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            partition_headers_count += 1
        print(f"Total ActivityPartitionHeaders: {partition_headers_count}")

        activity_swimlanes_count = 0
        for compartment in diagrams.findall(".//ActivitySwimlane2Compartment"):
            x = float(compartment.get('X', '0'))
            y = float(compartment.get('Y', '0'))
            width = float(compartment.get('Width', '0'))
            height = float(compartment.get('Height', '0'))
            name = compartment.get('Name')
            background_color = compartment.get('BackgroundColor', 'white')
            border_color = compartment.get('BorderColor', 'black')

            compartment_style = {
                'stroke': border_color,
                'fill': background_color,
                'stroke-width': 2
            }

            element_positions[activity_swimlanes_count] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, height), **compartment_style))

            if name:
                wrapped_lines = wrap_text_by_approx_width(name, width, 11)
                for i, line in enumerate(wrapped_lines):
                    text_y = y + 15 + i * 12
                    dwg.add(dwg.text(line, insert=(x + 5, text_y), fill='black', font_size=11, font_family='Arial',
                                     font_weight='normal'))

            activity_swimlanes_count += 1

        print(f"Total SwimLanesCompartment: {activity_swimlanes_count}")

        initial_nodes_count = 0
        # Find and place InitialNode
        for initial_node in diagrams.findall(".//InitialNode"):
            id = initial_node.get('Id')
            background = initial_node.get('Foreground')
            width = float(initial_node.get('Width', '0'))
            x = float(initial_node.get('X', '0'))
            y = float(initial_node.get('Y', '0'))

            radiuss = width / 4

            element_positions[id] = {
                'type': 'circle',
                'center': (x, y),
                'radius': radiuss
            }

            initial_node_style = {
                'fill': background,
            }

            dwg.add(dwg.circle(center=(x + 2 * radiuss, y + radiuss), r=radiuss, **initial_node_style))
            initial_nodes_count += 1
        print(f"Total InitialNodes: {initial_nodes_count}")

        activities_count = 0
        # Find and place Activities
        for activity in diagrams.findall(".//Activity"):
            id = activity.get('Id')
            x = float(activity.get('X', '0'))
            y = float(activity.get('Y', '0'))
            width = float(activity.get('Width', '200'))
            name = activity.get('Name')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, rect_height), **activity_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y + 15 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='bold'))

            activities_count += 1
        print(f"Total Activities: {activities_count}")

        actions_count = 0
        # Find and place ActivityAction
        for action in diagrams.findall(".//ActivityAction"):
            id = action.get('Id')
            x = float(action.get('X', '0'))
            y = float(action.get('Y', '0'))
            width = float(action.get('Width', '200'))
            height = float(action.get('Height', '40'))
            name = action.get('Name')
            background = action.get('Background', 'rgb(255, 255, 255)')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)
            rect_height = height

            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }

            background_style = {
                'stroke': 'black',
                'fill': background,
                'stroke-width': 1,
                'rx': 10,
                'ry': 10
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, rect_height), **background_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y + height / 2 - 3 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            actions_count += 1
        print(f"Total ActivityActions: {actions_count}")

        final_nodes_count = 0
        # Find and place FinalNode
        for final_node in diagrams.findall(".//ActivityFinalNode"):
            id = final_node.get('Id')
            background = final_node.get('Foreground')
            width = float(final_node.get('Width', '0'))
            x = float(final_node.get('X', '0'))
            y = float(final_node.get('Y', '0'))

            radius_outer = width / 2
            radius_inner = radius_outer * 0.6

            element_positions[id] = {
                'type': 'circle',
                'center': (x, y),
                'radius': radius_outer
            }

            final_node_outer_style = {
                'fill': 'none',
                'stroke': 'black',
                'stroke-width': 1
            }

            final_node_inner_style = {
                'fill': background,
                'stroke': 'none'
            }

            dwg.add(dwg.circle(center=(x + radius_outer, y + radius_outer), r=radius_outer, **final_node_outer_style))
            dwg.add(dwg.circle(center=(x + radius_outer, y + radius_outer), r=radius_inner, **final_node_inner_style))

            final_nodes_count += 1
        print(f"Total ActivityFinalNodes: {final_nodes_count}")

        accept_event_actions_count = 0
        # Find and place AcceptEventAction
        for accept_event in diagrams.findall(".//AcceptEventAction"):
            id = accept_event.get('Id')
            x = float(accept_event.get('X', '0'))
            y = float(accept_event.get('Y', '0'))
            rect_height = float(accept_event.get('Height', '0'))
            width = float(accept_event.get('Width', '200'))
            name = accept_event.get('Name')
            background = accept_event.get('Background', 'rgb(255, 255, 255)')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)

            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }

            arrow_size = width / 10
            arrow_points = [
                (x, y),
                (x + width, y),
                (x + width, y + rect_height),
                (x, y + rect_height),
                (x - arrow_size, y + rect_height),
                (x, y + rect_height / 2),
                (x - arrow_size, y)
            ]

            dwg.add(dwg.polygon(points=arrow_points, fill=background, stroke='black', stroke_width=1))

            for i, line in enumerate(wrapped_lines):
                text_y = y + 15 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            accept_event_actions_count += 1
        print(f"Total AcceptEventActions: {accept_event_actions_count}")

        send_signal_actions_count = 0
        # Find and place SendSignalAction
        for send_signal in diagrams.findall(".//SendSignalAction"):
            id = send_signal.get('Id')
            x = float(send_signal.get('X', '0'))
            y = float(send_signal.get('Y', '0'))
            rect_height = float(send_signal.get('Height', '0'))
            width = float(send_signal.get('Width', '200'))
            name = send_signal.get('Name')
            background = send_signal.get('Background', 'rgb(255, 255, 255)')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)

            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }
            arrow_size = rect_height

            arrow_points = [
                (x + width, y),
                (x, y),
                (x, y + rect_height),
                (x + width, y + rect_height),
                (x + width + arrow_size / 4, y + rect_height / 2)
            ]
            dwg.add(dwg.polygon(points=arrow_points, fill=background, stroke='black', stroke_width=1))

            for i, line in enumerate(wrapped_lines):
                text_y = y + 15 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))


            send_signal_actions_count += 1

        print(f"Total SendSignalActions: {send_signal_actions_count}")

        decision_nodes_count = 0
        # Find and place DecisionNode
        for decision_node in diagrams.findall(".//DecisionNode"):
            id = decision_node.get('Id')
            x = float(decision_node.get('X', '0')) + 2
            y = float(decision_node.get('Y', '0')) + 4
            width = float(decision_node.get('Width', '20')) - 4
            height = float(decision_node.get('Height', '40')) - 8

            half_width = width / 2
            half_height = height / 2
            points = [
                (x + half_width, y),
                (x + width, y + half_height),
                (x + half_width, y + height),
                (x, y + half_height)
            ]

            element_positions[id] = {
                'type': 'diamond',
                'center': (x, y),
                'width': width,
                'height': height,
                'points': points
            }
            dwg.add(dwg.polygon(points=points, **decision_node_style))

            decision_nodes_count += 1
        print(f"Total DecisionNodes: {decision_nodes_count}")

        object_nodes_count = 0
        # Find and place ObjectNode
        for object_node in diagrams.findall(".//ObjectNode"):
            id = object_node.get('Id')
            x = float(object_node.get('X', '0'))
            y = float(object_node.get('Y', '0'))
            width = float(object_node.get('Width', '85'))
            rect_height = float(object_node.get('Height', '40'))
            background = object_node.get('Background', 'rgb(122, 207, 245)')
            name = object_node.get('Name')
            text_len = width + 47
            wrapped_lines = wrap_text_by_approx_width(name, text_len, 11)

            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }

            background_style = {
                'stroke': 'black',
                'fill': background,
                'stroke-width': 1
            }

            dwg.add(dwg.rect(insert=(x, y), size=(width, rect_height), **background_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y + 15 + i * 12
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            object_nodes_count += 1
        print(f"Total ObjectNodes: {object_nodes_count}")

        control_flows_count = 0
        # Find and draw ControlFlows
        for control_flow in diagrams.findall(".//ControlFlow"):
            from_id = control_flow.get('From')
            to_id = control_flow.get('To')
            caption = control_flow.find('.//Caption')
            if caption is not None:
                x_caption = float(caption.get('X', '0')) + 30
                y_caption = float(caption.get('Y', '0')) + 10
                name = control_flow.get('Name')
                if name is not None:
                    dwg.add(dwg.text(name, insert=(x_caption, y_caption), fill='black', text_anchor='middle',
                                     font_size=11, font_family='Arial', font_weight='normal'))

            if from_id in element_positions and to_id in element_positions:

                points = control_flow.findall(".//Points/Point")
                points_list = [(float(point.get('X')), float(point.get('Y'))) for point in points]

                if len(points_list) >= 2:
                    for point in range(len(points_list)):
                        if point < len(points_list) - 1:
                            dwg.add(dwg.line(start=(points_list[point]), end=(points_list[point + 1]) , **connector_style))

                # Adding arrow heads
                if len(points_list) >= 2:
                    from_edge = points_list[-2]
                    to_edge = points_list[-1]
                    arrow_size = 15
                    angle = math.atan2(to_edge[1] - from_edge[1], to_edge[0] - from_edge[0])
                    arrow_points = [
                        (to_edge[0] - arrow_size * math.cos(angle - math.pi / 6),
                         to_edge[1] - arrow_size * math.sin(angle - math.pi / 6)),
                        (to_edge[0] - arrow_size * math.cos(angle + math.pi / 6),
                         to_edge[1] - arrow_size * math.sin(angle + math.pi / 6)),
                        to_edge
                    ]
                    dwg.add(dwg.line(start=(arrow_points[0]), end=(arrow_points[2]),  **connector_style))
                    dwg.add(dwg.line(start=(arrow_points[1]), end=(arrow_points[2]),  **connector_style))

                control_flows_count += 1

        print(f"Total ControlFlows: {control_flows_count}")

        activity_object_flow_count = 0
        for activity_object_flow in diagrams.findall(".//ActivityObjectFlow"):
            from_id = activity_object_flow.get('From')
            to_id = activity_object_flow.get('To')
            caption = activity_object_flow.find('.//Caption')
            if caption is not None:
                x_caption = float(caption.get('X', '0')) + 30
                y_caption = float(caption.get('Y', '0')) + 10
                name = activity_object_flow.get('Name')
                if name is not None:
                    dwg.add(dwg.text(name, insert=(x_caption, y_caption), fill='black', text_anchor='middle',
                                     font_size=11, font_family='Arial', font_weight='normal'))

            if from_id in element_positions and to_id in element_positions:
                from_element = element_positions[from_id]
                to_element = element_positions[to_id]

                # Check if there are points defined in XML
                points = activity_object_flow.findall(".//Points/Point")
                points_list = [(float(point.get('X')), float(point.get('Y'))) for point in points]

                if len(points_list) >= 2:
                    # Draw the line using the extracted points
                    for point_idx in range(len(points_list) - 1):
                        start_point = points_list[point_idx]
                        end_point = points_list[point_idx + 1]
                        dwg.add(dwg.line(start=start_point, end=end_point, **connector_style))

                if len(points_list) >= 2:
                    from_edge = points_list[-2]
                    to_edge = points_list[-1]
                    arrow_size = 15
                    angle = math.atan2(to_edge[1] - from_edge[1], to_edge[0] - from_edge[0])
                    arrow_points = [
                        (to_edge[0] - arrow_size * math.cos(angle - math.pi / 6),
                         to_edge[1] - arrow_size * math.sin(angle - math.pi / 6)),
                        (to_edge[0] - arrow_size * math.cos(angle + math.pi / 6),
                         to_edge[1] - arrow_size * math.sin(angle + math.pi / 6)),
                        to_edge
                    ]
                    dwg.add(dwg.line(start=(arrow_points[0]), end=(arrow_points[2]), **connector_style))
                    dwg.add(dwg.line(start=(arrow_points[1]), end=(arrow_points[2]), **connector_style))

                activity_object_flow_count += 1
        print(f"Total ControlFlows: {activity_object_flow_count}")

        dwg.save()

    except Exception as e:
        print(f"Error processing XML and generating SVG: {e}")


def calculate_edge(from_element, to_element):
    """Calculate the point on the edge of the from_element closest to the to_element."""
    if from_element['type'] == 'rect':
        from_center = (from_element['x'] + from_element['width'] / 2, from_element['y'])
    elif from_element['type'] == 'circle':
        from_center = from_element['center']
    elif from_element['type'] == 'diamond':
        from_center = from_element['center']

    if to_element['type'] == 'rect':
        to_center = (to_element['x'] + to_element['width'] / 2, to_element['y'])
    elif to_element['type'] == 'circle':
        to_center = to_element['center']
    elif to_element['type'] == 'diamond':
        to_center = to_element['center']

    dx = to_center[0] - from_center[0]
    dy = to_center[1] - from_center[1]

    if from_element['type'] == 'rect':
        half_width = from_element['width'] / 2
        half_height = from_element['height'] / 2

        if abs(dx) > abs(dy):
            if dx > 0:
                return (from_center[0] + half_width, from_center[1])
            else:
                return (from_center[0] - half_width, from_center[1])
        else:
            if dy > 0:
                return (from_center[0], from_center[1] + half_height)
            else:
                return (from_center[0], from_center[1] - half_height)
    elif from_element['type'] == 'circle':
        radius = from_element['radius']
        angle = math.atan2(dy, dx)
        return (from_center[0] + radius * math.cos(angle), from_center[1] + radius * math.sin(angle))
    elif from_element['type'] == 'diamond':
        half_width = from_element['width'] / 2
        half_height = from_element['height'] / 2

        if abs(dx) > abs(dy):
            if dx > 0:
                return (from_center[0] + half_width, from_center[1])
            else:
                return (from_center[0] - half_width, from_center[1])
        else:
            if dy > 0:
                return (from_center[0], from_center[1] + half_height)
            else:
                return (from_center[0], from_center[1] - half_height)


if __name__ == "__main__":
    xml_input_file = 'sumxmls/simple_activity2_hard.xml'
    svg_output_file = 'activity_diagram.svg'

    parse_xml_to_svg(xml_input_file, svg_output_file)

