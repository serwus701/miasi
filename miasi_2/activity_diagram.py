import xml.etree.ElementTree as ET
import svgwrite
from xml.sax.saxutils import escape
import textwrap

def calculate_text_height(text, width, font_size):
    wrapped_text = textwrap.fill(text, width=15)
    lines = wrapped_text.splitlines()
    return len(lines) * font_size * 1.2  # Assuming font-size * 1.2 as line height

def convert_xml_to_svg(xml_file, output_svg):
    # Parse XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find all Activity elements in Models section
    models = root.find('Diagrams')
    if models is None:
        raise ValueError("No 'Models' section found in XML.")

    activities = models.findall('.//Activity')
    actions = models.findall('.//ActivityAction')
    initialNodes = models.findall('.//InitialNode')
    finalNodes = models.findall('.//ActivityFinalNode')

    # Initialize SVG drawing
    dwg = svgwrite.Drawing(output_svg, profile='tiny')

    # Define styles for elements
    styles = {
        'activity': {'fill': 'rgb(122, 207, 245)', 'stroke': 'black', 'stroke-width': '1px'},
        'action': {'fill': 'rgb(122, 207, 245)', 'stroke': 'black', 'stroke-width': '1px'},
        'control_flow': {'stroke': 'black', 'stroke-width': '1px'},
        'initial_node': {'fill': 'black', 'stroke': 'black', 'stroke-width': '1px'}
    }

    font_size = 12  # Example font size for text

    # Draw activities and their control flows
    offset = 0  # Initial offset for drawing activities
    for activity in activities:
        # Draw activity node
        activity_id = activity.attrib.get('Id', None)
        activity_name = activity.attrib.get('Name', None)
        activity_x = activity.attrib.get('Name', None)
        activity_y = activity.attrib.get('Name', None)
        if activity_id is None:
            print(f"Warning: 'Id' attribute not found in activity: {activity}")
            continue

        x = 100 + offset * 200  # Example x position with offset
        y = 100  # Example y position

        # Calculate text height based on wrapped text
        if activity_name:
            text_height = calculate_text_height(activity_name, width=15, font_size=font_size)
        else:
            text_height = font_size  # Default height if no text

        dwg.add(dwg.rect(insert=(x, y), size=(170, text_height), **styles['activity']))

        # Escape and wrap activity_name before adding text to SVG
        if activity_name:
            wrapped_name = textwrap.fill(activity_name, width=15)
            escaped_activity_name = escape(wrapped_name)
            lines = escaped_activity_name.splitlines()
            for i, line in enumerate(lines):
                dwg.add(dwg.text(line, insert=(x + 10, y + 20 + i * font_size), fill='black'))  # Add wrapped text to activity

        # Draw control flows
        from_relationships = activity.findall('.//FromSimpleRelationships/ControlFlow')
        for relation in from_relationships:
            to_activity_id = relation.attrib.get('To', None)
            if to_activity_id is None:
                print(f"Warning: 'To' attribute not found in relation: {relation}")
                continue

            # Find corresponding 'To' activity and calculate its position
            to_activity = models.find(f".//Activity[@Id='{to_activity_id}']")
            if to_activity is None:
                print(f"Warning: 'To' activity with ID '{to_activity_id}' not found.")
                continue

            to_index = activities.index(to_activity)
            to_x = 100 + to_index * 200  # Example x position for 'To' activity
            to_y = 100  # Example y position

            # Example: draw a line between activities based on calculated positions
            dwg.add(dwg.line(start=(x + 100, y + text_height), end=(to_x, to_y + text_height), **styles['control_flow']))

        offset += 1  # Increment offset for next activity

    # Draw actions and their control flows
    for action in actions:
        # Draw action node
        action_id = action.attrib.get('Id', None)
        action_name = action.attrib.get('Name', None)
        if action_id is None:
            print(f"Warning: 'Id' attribute not found in action: {action}")
            continue

        x = 100 + offset * 200  # Example x position with offset
        y = 100  # Example y position

        # Calculate text height based on wrapped text
        if action_name:
            text_height = calculate_text_height(action_name, width=15, font_size=font_size)
        else:
            text_height = font_size  # Default height if no text

        dwg.add(dwg.rect(insert=(x, y), size=(170, text_height + 20), **styles['action']))

        # Escape and wrap action_name before adding text to SVG
        if action_name:
            wrapped_name = textwrap.fill(action_name, width=15)
            escaped_action_name = escape(wrapped_name)
            lines = escaped_action_name.splitlines()
            for i, line in enumerate(lines):
                dwg.add(dwg.text(line, insert=(x + 10, y + 20 + i * font_size), fill='black'))  # Add wrapped text to action

        # Draw control flows
        from_relationships = action.findall('.//FromSimpleRelationships/ControlFlow')
        for relation in from_relationships:
            to_action_id = relation.attrib.get('To', None)
            if to_action_id is None:
                print(f"Warning: 'To' attribute not found in relation: {relation}")
                continue

            # Find corresponding 'To' action and calculate its position
            to_action = models.find(f".//ActivityAction[@Id='{to_action_id}']")
            if to_action is None:
                print(f"Warning: 'To' action with ID '{to_action_id}' not found.")
                continue

            to_index = actions.index(to_action)
            to_x = 100 + to_index * 200  # Example x position for 'To' action
            to_y = 100  # Example y position

            # Example: draw a line between actions based on calculated positions
            dwg.add(dwg.line(start=(x + 100, y + text_height), end=(to_x, to_y + text_height), **styles['control_flow']))

        offset += 1  # Increment offset for next action

    # Draw initial nodes (black dots)
    initial_offset = offset  # Save initial offset for initial nodes
    for initialNode in initialNodes:
        x = 100 + initial_offset * 200  # Example x position with offset
        y = 100  # Example y position
        dwg.add(dwg.circle(center=(x + 50, y + 25), r=5, **styles['initial_node']))  # Draw a black circle for initialNode
        initial_offset += 1  # Increment offset for next initialNode

    # Save SVG file
    dwg.save()


# Example usage:
if __name__ == "__main__":
    xml_file = 'sumxmls/simple_activity_simple.xml'  # Ścieżka do pliku XML
    svg_file = 'diagram.svg'  # Ścieżka do pliku SVG, do którego zapisujemy wynik

    convert_xml_to_svg(xml_file, svg_file)
