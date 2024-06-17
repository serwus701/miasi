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
            'x': int(accept_event.get('X', x_offset)),
            'y': int(accept_event.get('Y', current_y)) - rect_height / 2,
            'width': int(accept_event.get('Width', 200)),
            'height': rect_height
        }

        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(int(accept_event.get('X', x_offset)), int(accept_event.get('Y', current_y)) - rect_height / 2), size=(int(accept_event.get('Width', 200)), rect_height), **background_style))

        for i, line in enumerate(wrapped_lines):
            text_y = int(accept_event.get('Y', current_y)) - rect_height / 2 + 15 + i * 12
            dwg.add(dwg.text(line, insert=(int(accept_event.get('X', x_offset)) + int(accept_event.get('Width', 200)) / 2, text_y), fill='black', text_anchor='middle'))

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
            'x': int(send_signal.get('X', x_offset)),
            'y': int(send_signal.get('Y', current_y)) - rect_height / 2,
            'width': int(send_signal.get('Width', 200)),
            'height': rect_height
        }

        background_style = {
            'stroke': 'black',
            'fill': background,
            'stroke-width': 2
        }

        dwg.add(dwg.rect(insert=(int(send_signal.get('X', x_offset)), int(send_signal.get('Y', current_y)) - rect_height / 2), size=(int(send_signal.get('Width', 200)), rect_height), **background_style))

        for i, line in enumerate(wrapped_lines):
            text_y = int(send_signal.get('Y', current_y)) - rect_height / 2 + 15 + i * 12
            dwg.add(dwg.text(line, insert=(int(send_signal.get('X', x_offset)) + int(send_signal.get('Width', 200)) / 2, text_y), fill='black', text_anchor='middle'))

        current_y += element_spacing + (len(wrapped_lines) - 1) * 12
        send_signal_actions_count += 1
    print(f"Total SendSignalActions: {send_signal_actions_count}")

    # Now draw connectors between elements
    for connector in diagrams.findall(".//Connector"):
        start_id = connector.get('Start')
        end_id = connector.get('End')

        if start_id in element_positions and end_id in element_positions:
            start_type = element_positions[start_id]['type']
            end_type = element_positions[end_id]['type']

            if start_type == 'circle':
                start_x, start_y = element_positions[start_id]['center']
            else:
                start_x = element_positions[start_id]['x'] + element_positions[start_id]['width']
                start_y = element_positions[start_id]['y'] + element_positions[start_id]['height'] / 2

            if end_type == 'circle':
                end_x, end_y = element_positions[end_id]['center']
            else:
                end_x = element_positions[end_id]['x']
                end_y = element_positions[end_id]['y'] + element_positions[end_id]['height'] / 2

            # Calculate connector path
            path = dwg.path(d=('M', start_x, start_y, 'L', end_x, end_y), **connector_style)
            dwg.add(path)

    # Save SVG file
    dwg.save()

if __name__ == "__main__":
    xml_input_file = 'sumxmls/simple_activity.xml'
    svg_output_file = 'activity_diagram.svg'

    parse_xml_to_svg(xml_input_file, svg_output_file)

