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
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    diagrams = root.find('Diagrams')
    # Create an SVG drawing
    dwg = svgwrite.Drawing(svg_file, profile='full')

    # Define some basic styles
    activity_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
    initial_node_style = {'fill': 'black'}
    final_node_style = {'fill': 'red'}
    accept_event_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
    send_signal_style = {'stroke': 'black', 'fill': 'white', 'stroke-width': 2}
    connector_style = {'stroke': 'black', 'stroke-width': 1}
    text_max_length = 20  # Max characters per line for wrapped text

    # Map elements to positions and their sizes
    element_positions = {}
    current_y = 20  # Starting Y position
    element_spacing = 60  # Space between elements, increased to fit text wrapping
    x_offset = 70  # X coordinate alignment for all elements

    # Debug information
    initial_nodes_count = 0
    # Find and place InitialNode
    for initial_node in diagrams.findall(".//InitialNode"):
        id = initial_node.get('Id')
        element_positions[id] = {
            'type': 'circle',
            'center': (x_offset, current_y),  # Align horizontally with other elements
            'radius': 5
        }
        dwg.add(dwg.circle(center=(x_offset, current_y), r=5, **initial_node_style))
        current_y += element_spacing
        initial_nodes_count += 1
    print(f"Total InitialNodes: {initial_nodes_count}")

    activities_count = 0
    # Find and place Activities
    for activity in diagrams.findall(".//Activity"):
        id = activity.get('Id')
        name = activity.get('Name')
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = {
            'type': 'rect',
            'x': x_offset,
            'y': current_y - rect_height / 2,
            'width': 200,
            'height': rect_height
        }

        dwg.add(dwg.rect(insert=(x_offset, current_y - rect_height / 2), size=(200, rect_height), **activity_style))

        for i, line in enumerate(wrapped_lines):
            text_y = current_y - rect_height / 2 + 15 + i * 12  # Adjust Y for each line
            dwg.add(dwg.text(line, insert=(x_offset + 100, text_y), fill='black', text_anchor='middle'))

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12  # Adjust spacing for wrapped text
        activities_count += 1
    print(f"Total Activities: {activities_count}")

    actions_count = 0
    # Find and place ActivityAction
    for action in diagrams.findall(".//ActivityAction"):
        id = action.get('Id')
        name = action.get('Name')
        background = action.get('Background', 'rgb(255, 255, 255)')  # Default to white if not specified
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = {
            'type': 'rect',
            'x': x_offset,
            'y': current_y - rect_height / 2,
            'width': 200,
            'height': rect_height
        }

        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(x_offset, current_y - rect_height / 2), size=(200, rect_height), **background_style))

        for i, line in enumerate(wrapped_lines):
            text_y = current_y - rect_height / 2 + 15 + i * 12
            dwg.add(dwg.text(line, insert=(x_offset + 100, text_y), fill='black', text_anchor='middle'))

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12
        actions_count += 1
    print(f"Total ActivityActions: {actions_count}")

    final_nodes_count = 0
    # Find and place FinalNode
    for final_node in diagrams.findall(".//ActivityFinalNode"):
        id = final_node.get('Id')
        element_positions[id] = {
            'type': 'circle',
            'center': (x_offset, current_y),  # Align horizontally with other elements
            'radius': 5
        }
        dwg.add(dwg.circle(center=(x_offset, current_y), r=5, **final_node_style))
        current_y += element_spacing
        final_nodes_count += 1
    print(f"Total ActivityFinalNodes: {final_nodes_count}")

    accept_event_actions_count = 0
    # Find and place AcceptEventAction
    for accept_event in diagrams.findall(".//AcceptEventAction"):
        id = accept_event.get('Id')
        name = accept_event.get('Name')
        background = accept_event.get('Background', 'rgb(255, 255, 255)')  # Default to white if not specified
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = {
            'type': 'rect',
            'x': x_offset,
            'y': current_y - rect_height / 2,
            'width': 200,
            'height': rect_height
        }

        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(x_offset, current_y - rect_height / 2), size=(200, rect_height), **accept_event_style))

        for i, line in enumerate(wrapped_lines):
            text_y = current_y - rect_height / 2 + 15 + i * 12
            dwg.add(dwg.text(line, insert=(x_offset + 100, text_y), fill='black', text_anchor='middle'))

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12
        accept_event_actions_count += 1
    print(f"Total AcceptEventActions: {accept_event_actions_count}")

    send_signal_actions_count = 0
    # Find and place SendSignalAction
    for send_signal in diagrams.findall(".//SendSignalAction"):
        id = send_signal.get('Id')
        name = send_signal.get('Name')
        background = send_signal.get('Background', 'rgb(255, 255, 255)')  # Default to white if not specified
        wrapped_lines = wrap_text(name, text_max_length)

        rect_height = 20 + (len(wrapped_lines) - 1) * 12  # Adjust height based on wrapped lines
        element_positions[id] = {
            'type': 'rect',
            'x': x_offset,
            'y': current_y - rect_height / 2,
            'width': 200,
            'height': rect_height
        }

        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(x_offset, current_y - rect_height / 2), size=(200, rect_height), **background_style))
        for i, line in enumerate(wrapped_lines):
            text_y = current_y - rect_height / 2 + 15 + i * 12
            dwg.add(dwg.text(line, insert=(x_offset + 100, text_y), fill='black', text_anchor='middle'))

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12
        send_signal_actions_count += 1
    print(f"Total SendSignalActions: {send_signal_actions_count}")

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
            arrow_size = 5
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

    # Save the SVG file
    dwg.save()


def calculate_edge(from_element, to_element):
    """Calculate the point on the edge of the from_element closest to the to_element."""
    if from_element['type'] == 'rect':
        from_center = (from_element['x'] + from_element['width'] / 2, from_element['y'] + from_element['height'] / 2)
    elif from_element['type'] == 'circle':
        from_center = from_element['center']

    if to_element['type'] == 'rect':
        to_center = (to_element['x'] + to_element['width'] / 2, to_element['y'] + to_element['height'] / 2)
    elif to_element['type'] == 'circle':
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

if __name__ == "__main__":
    xml_input_file = 'sumxmls/simple_activity.xml'
    svg_output_file = 'activity_diagram.svg'

    parse_xml_to_svg(xml_input_file, svg_output_file)
