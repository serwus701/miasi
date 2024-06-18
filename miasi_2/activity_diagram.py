import math
import xml.etree.ElementTree as ET
import svgwrite


def wrap_text(text, max_length):
    """Wrap text into lines that fit within the given max_length, including breaking long words."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        while len(word) > max_length:
            # Add part of the long word to the current line and create a new one for the rest
            current_line.append(word[:max_length])
            lines.append(" ".join(current_line))
            word = word[max_length:]
            current_line = []
            current_length = 0

        if current_length + len(word) + (1 if current_line else 0) <= max_length:
            current_line.append(word)
            current_length += len(word) + (1 if current_line else 0)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def parse_xml_to_svg(xml_file, svg_file):
    try:
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        diagrams = root.find('Diagrams')
        # Create an SVG drawing
        dwg = svgwrite.Drawing(svg_file, profile='full')

        # Define some basic styles
        activity_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2, 'rx': 10, 'ry': 10}
        initial_node_style = {'fill': 'black'}
        final_node_style = {'fill': 'red'}
        accept_event_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
        send_signal_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
        decision_node_style = {'stroke': 'black', 'fill': 'rgb(122, 207, 245)', 'stroke-width': 2}
        object_node_style = {'stroke': 'black', 'fill': 'rgb(122, 207, 245)', 'stroke-width': 2}
        connector_style = {'stroke': 'black', 'stroke-width': 1}
        text_max_length = 20  # Max characters per line for wrapped text

        element_positions = {}  # Map to store positions and sizes

        # Debug information
        initial_nodes_count = 0
        # Find and place InitialNode
        for initial_node in diagrams.findall(".//InitialNode"):
            id = initial_node.get('Id')
            x = float(initial_node.get('X', '0'))
            y = float(initial_node.get('Y', '0'))

            element_positions[id] = {
                'type': 'circle',
                'center': (x, y),
                'radius': 5
            }
            dwg.add(dwg.circle(center=(x, y), r=5, **initial_node_style))
            initial_nodes_count += 1
        print(f"Total InitialNodes: {initial_nodes_count}")

        activities_count = 0
        # Find and place Activities
        for activity in diagrams.findall(".//Activity"):
            id = activity.get('Id')
            x = float(activity.get('X', '0'))
            y = float(activity.get('Y', '0'))
            width = float(activity.get('Width', '200'))  # Default width
            name = activity.get('Name')
            wrapped_lines = wrap_text(name, text_max_length)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
            element_positions[id] = {
                'type': 'rect',
                'x': x,
                'y': y,
                'width': width,
                'height': rect_height
            }

            dwg.add(dwg.rect(insert=(x, y - rect_height / 2), size=(width, rect_height), **activity_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y - rect_height / 2 + 15 + i * 12
                # Adjust text size and other properties here
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
            width = float(action.get('Width', '200'))  # Default width
            name = action.get('Name')
            background = action.get('Background', 'rgb(255, 255, 255)')
            wrapped_lines = wrap_text(name, text_max_length)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
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
                'stroke-width': 2,
                'rx': 10,
                'ry': 10
            }

            dwg.add(dwg.rect(insert=(x, y - rect_height / 2), size=(width, rect_height), **background_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y - rect_height / 2 + 15 + i * 12
                # Adjust text size and other properties here
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            actions_count += 1
        print(f"Total ActivityActions: {actions_count}")

        final_nodes_count = 0
        # Find and place FinalNode
        for final_node in diagrams.findall(".//ActivityFinalNode"):
            id = final_node.get('Id')
            x = float(final_node.get('X', '0'))
            y = float(final_node.get('Y', '0'))

            element_positions[id] = {
                'type': 'circle',
                'center': (x, y),
                'radius': 5
            }
            dwg.add(dwg.circle(center=(x, y), r=5, **final_node_style))
            final_nodes_count += 1
        print(f"Total ActivityFinalNodes: {final_nodes_count}")

        accept_event_actions_count = 0
        # Find and place AcceptEventAction
        for accept_event in diagrams.findall(".//AcceptEventAction"):
            id = accept_event.get('Id')
            x = float(accept_event.get('X', '0'))
            y = float(accept_event.get('Y', '0'))
            width = float(accept_event.get('Width', '200'))  # Default width
            name = accept_event.get('Name')
            background = accept_event.get('Background', 'rgb(255, 255, 255)')
            wrapped_lines = wrap_text(name, text_max_length)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
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
                'stroke-width': 2
            }

            arrow_size = width / 10  # Adjust as needed

            # Define points for the arrow on the right side
            arrow_points = [
                # (x, y - rect_height / 2),
                (x, y - rect_height / 2),
                (x + width, y - rect_height / 2),
                (x + width, y + rect_height / 2),
                (x, y + rect_height / 2),
                (x - arrow_size, y + rect_height / 2),
                (x, y),
                (x - arrow_size, y - rect_height / 2)
                # (x, y - arrow_size / 2),  # Top point of the arrow
                # (x, y + arrow_size / 2),  # Bottom point of the arrow
                # (x - arrow_size, y)  # Tip of the arrow
            ]

            # dwg.add(
                # dwg.rect(insert=(x, y - rect_height / 2), size=(width + arrow_size, rect_height), **background_style))
            dwg.add(dwg.polygon(points=arrow_points, fill=background, stroke='black', stroke_width=2))

            for i, line in enumerate(wrapped_lines):
                text_y = y - rect_height / 2 + 15 + i * 12
                # Adjust text size and other properties here
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            # Adding small arrow from left

            accept_event_actions_count += 1
        print(f"Total AcceptEventActions: {accept_event_actions_count}")

        send_signal_actions_count = 0
        # Find and place SendSignalAction
        for send_signal in diagrams.findall(".//SendSignalAction"):
            id = send_signal.get('Id')
            x = float(send_signal.get('X', '0'))
            y = float(send_signal.get('Y', '0'))
            width = float(send_signal.get('Width', '200'))  # Default width
            name = send_signal.get('Name')
            background = send_signal.get('Background', 'rgb(255, 255, 255)')
            wrapped_lines = wrap_text(name, text_max_length)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
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
                'stroke-width': 2
            }

            # Calculate arrow size based on the width of the rectangle
            arrow_size = rect_height  # Adjust as needed

            # Define points for the arrow on the right side
            arrow_points = [
                (x + width, y - rect_height / 2),
                (x, y - rect_height / 2),
                (x, y + rect_height / 2),
                (x + width, y + rect_height / 2),
                # (x + width + arrow_size, y - arrow_size / 2),  # Top point of the arrow
                # (x + width + arrow_size, y + arrow_size / 2),  # Bottom point of the arrow
                (x + width + arrow_size, y)  # Tip of the arrow
            ]

            # Draw the background rectangle including the arrow
            # Adjust the size of the rectangle to include the arrow
            # dwg.add(
            #     dwg.rect(insert=(x, y - rect_height / 2), size=(width + arrow_size, rect_height), **background_style))
            # Draw the arrow
            dwg.add(dwg.polygon(points=arrow_points, fill=background, stroke='black', stroke_width=2))

            for i, line in enumerate(wrapped_lines):
                text_y = y - rect_height / 2 + 15 + i * 12
                # Adjust text size and other properties here
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))


            send_signal_actions_count += 1

        print(f"Total SendSignalActions: {send_signal_actions_count}")

        decision_nodes_count = 0
        # Find and place DecisionNode
        for decision_node in diagrams.findall(".//DecisionNode"):
            id = decision_node.get('Id')
            x = float(decision_node.get('X', '0'))
            y = float(decision_node.get('Y', '0'))
            background = decision_node.get('Background', 'rgb(122, 207, 245)')  # Default to the specified blue
            width = float(decision_node.get('Width', '40'))  # Default width
            height = float(decision_node.get('Height', '40'))  # Default height

            # Calculate the points of the diamond (centered at the current_y position)
            half_width = width / 2
            half_height = height / 2
            points = [
                (x, y - half_height),  # Top
                (x + half_width, y),  # Right
                (x, y + half_height),  # Bottom
                (x - half_width, y)  # Left
            ]

            element_positions[id] = {
                'type': 'diamond',
                'center': (x, y),
                'width': width,
                'height': height,
                'points': points
            }

            # Draw the diamond shape
            dwg.add(dwg.polygon(points=points, **decision_node_style))

            decision_nodes_count += 1
        print(f"Total DecisionNodes: {decision_nodes_count}")

        object_nodes_count = 0
        # Find and place ObjectNode
        for object_node in diagrams.findall(".//ObjectNode"):
            id = object_node.get('Id')
            x = float(object_node.get('X', '0'))
            y = float(object_node.get('Y', '0'))
            width = float(object_node.get('Width', '85'))  # Default width
            height = float(object_node.get('Height', '40'))  # Default height
            background = object_node.get('Background', 'rgb(122, 207, 245)')  # Default background color
            name = object_node.get('Name')
            wrapped_lines = wrap_text(name, text_max_length)

            rect_height = 20 + (len(wrapped_lines) - 1) * 12
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
                'stroke-width': 2
            }

            dwg.add(dwg.rect(insert=(x, y - rect_height / 2), size=(width, rect_height), **background_style))

            for i, line in enumerate(wrapped_lines):
                text_y = y - rect_height / 2 + 15 + i * 12
                # Adjust text size and other properties here
                dwg.add(dwg.text(line, insert=(x + width / 2, text_y), fill='black', text_anchor='middle',
                                 font_size=11, font_family='Arial', font_weight='normal'))

            object_nodes_count += 1
        print(f"Total ObjectNodes: {object_nodes_count}")

        control_flows_count = 0
        # Find and draw ControlFlows
        for control_flow in diagrams.findall(".//ControlFlow"):
            from_id = control_flow.get('From')
            to_id = control_flow.get('To')

            if from_id in element_positions and to_id in element_positions:
                from_element = element_positions[from_id]
                to_element = element_positions[to_id]

                # Calculate the edge point closest to the other element
                from_edge = calculate_edge(from_element, to_element)
                to_edge = calculate_edge(to_element, from_element)

                # Draw the line
                dwg.add(dwg.line(start=from_edge, end=to_edge, **connector_style))

                # Adding arrow heads
                arrow_size = 7
                angle = math.atan2(to_edge[1] - from_edge[1], to_edge[0] - from_edge[0])
                arrow_points = [
                    (to_edge[0] - arrow_size * math.cos(angle - math.pi / 6),
                     to_edge[1] - arrow_size * math.sin(angle - math.pi / 6)),
                    (to_edge[0] - arrow_size * math.cos(angle + math.pi / 6),
                     to_edge[1] - arrow_size * math.sin(angle + math.pi / 6)),
                    to_edge
                ]
                dwg.add(dwg.polygon(points=arrow_points, fill='black'))
                control_flows_count += 1
        print(f"Total ControlFlows: {control_flows_count}")

        activity_object_flow_count = 0
        for activity_object_flow in diagrams.findall(".//ActivityObjectFlow"):
            from_id = activity_object_flow.get('From')
            to_id = activity_object_flow.get('To')

            if from_id in element_positions and to_id in element_positions:
                from_element = element_positions[from_id]
                to_element = element_positions[to_id]

                # Calculate the edge point closest to the other element
                from_edge = calculate_edge(from_element, to_element)
                to_edge = calculate_edge(to_element, from_element)

                # Draw the line
                dwg.add(dwg.line(start=from_edge, end=to_edge, **connector_style))

                # Adding arrow heads
                arrow_size = 7
                angle = math.atan2(to_edge[1] - from_edge[1], to_edge[0] - from_edge[0])
                arrow_points = [
                    (to_edge[0] - arrow_size * math.cos(angle - math.pi / 6),
                     to_edge[1] - arrow_size * math.sin(angle - math.pi / 6)),
                    (to_edge[0] - arrow_size * math.cos(angle + math.pi / 6),
                     to_edge[1] - arrow_size * math.sin(angle + math.pi / 6)),
                    to_edge
                ]
                dwg.add(dwg.polygon(points=arrow_points, fill='black'))
                activity_object_flow_count += 1
        print(f"Total ControlFlows: {activity_object_flow_count}")

        # Save the SVG file
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
                # Connect to the right edge center
                return (from_center[0] + half_width, from_center[1])
            else:
                # Connect to the left edge center
                return (from_center[0] - half_width, from_center[1])
        else:
            if dy > 0:
                # Connect to the bottom edge center
                return (from_center[0], from_center[1] + half_height)
            else:
                # Connect to the top edge center
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
                # Right edge
                return (from_center[0] + half_width, from_center[1])
            else:
                # Left edge
                return (from_center[0] - half_width, from_center[1])
        else:
            if dy > 0:
                # Bottom edge
                return (from_center[0], from_center[1] + half_height)
            else:
                # Top edge
                return (from_center[0], from_center[1] - half_height)


if __name__ == "__main__":
    xml_input_file = 'sumxmls/simple_activity3_medium.xml'
    svg_output_file = 'activity_diagram.svg'

    parse_xml_to_svg(xml_input_file, svg_output_file)

