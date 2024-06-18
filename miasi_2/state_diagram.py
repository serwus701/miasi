import lxml.etree as ET
import svgwrite


def parse_model_children(elem):
    """ Parse the ModelChildren elements and return their text content. """
    children_text = ""
    for child in elem:
        if child.tag.endswith('ModelChildren'):
            for subchild in child:
                if 'Name' in subchild.attrib:
                    children_text += subchild.attrib['Name'] + "\n"
    return children_text.strip()

def parse_caption_pos(elem):
    for child in elem:
        if child.tag.endswith('Caption'):
            x = int(child.attrib.get('X'))
            y = int(child.attrib.get('Y'))
            height = int(elem.attrib.get('Height', 0))
            width = int(elem.attrib.get('Width', 0))
            return {'height':height, 'width':width, 'x': x, 'y': y}
    return {'x': 0, 'y': 0}

def parse_font_shift(elem):
    shift = 0
    for child in elem:
        if child.tag.endswith('ElementFont'):
            shift += int(child.attrib.get('Size'))
    return shift


def get_state_name(elem):
    """ Retrieve the state's name, considering potential translations or alternate formats. """
    return elem.attrib.get('Name', 'Unnamed')


def rgb_to_hex(rgb_string):
    # Remove the "rgb(" and ")" part and split the remaining string by commas
    rgb_values = rgb_string[4:-1].split(',')

    # Convert each component to an integer
    r, g, b = [int(value) for value in rgb_values]

    # Format the integers as hexadecimal and return the combined string
    return f'#{r:02X}{g:02X}{b:02X}'

def parse(xml_file, output_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # SVG setup
    dwg = svgwrite.Drawing(output_file, profile='full', size=('1000px', '800px'))

    # Define arrow marker for transitions
    arrow_marker = dwg.marker(id='arrow', insert=(10, 5), size=(10, 10), orient='auto')
    arrow_marker.add(dwg.path(d='M0,0 L0,10 L10,5 Z', fill='black'))
    dwg.defs.add(arrow_marker)

    # Extracting state machine elements
    states = {}
    transitions = []
    special_states = {}
    points = {}

    # Parse states and transitions
    for elem in root.iter():
        if 'State' in elem.tag:
            state_id = elem.attrib.get('Id', None)
            state_name = get_state_name(elem)
            state_x = int(elem.attrib.get('X', 0))
            state_y = int(elem.attrib.get('Y', 0))
            height = int(elem.attrib.get('Height', 0))
            width = int(elem.attrib.get('Width', 0))
            color = rgb_to_hex(elem.attrib.get('Background', 'rgb(0,0,0)'))
            model_children = parse_model_children(elem)
            align_to_grid = elem.attrib.get('AlignToGrid')
            font_shift_y = int(parse_font_shift(elem))
            print(parse_caption_pos(elem))
            print(
                f'Parsed state: ID={state_id}, Name={state_name}, X={state_x}, Y={state_y}, ModelChildren={model_children}, Width={width}, Height={height}')
            if state_x == 0.0 and state_y == 0.0 and state_id and len(model_children) > 0 and align_to_grid is None:
                special_states[state_id] = {'name': state_name, 'children': model_children, 'caption': parse_caption_pos(elem)}
            elif state_id and align_to_grid is None:
                print('xd')
                states[state_id] = {'name': state_name, 'x': state_x, 'y': state_y, 'children': model_children,
                                    'height': height, 'width': width, 'caption': parse_caption_pos(elem), 'fontShift': font_shift_y, 'color': color}
        elif elem.tag == 'Transition2':
            x = int(elem.attrib.get('X',0))
            y = int(elem.attrib.get('Y',0))
            transition_name = elem.attrib.get('Name', '')
            id = elem.attrib.get('Id', '')
            print(f'Parsed transition: Id={id}, X={x}, Y={y}, Name={transition_name}')
            if x and y and id:
                transitions.append({'id': id, 'x': x, 'y': y, 'name': transition_name})
        elif elem.tag == 'Points':
            pointPoints = []
            for child in elem.iterchildren():
                x = child.attrib.get('X')
                y = child.attrib.get('Y')
                pointPoints.append({'x': x, 'y': y})
            points[elem.getparent().attrib.get('Id')] = pointPoints

    # Integrate special states into their parent states
    for special_state_id, special_state_info in special_states.items():
        for parent_id, parent_info in states.items():
            if special_state_info['name'] in parent_info['name']:
                print(f'Parent: {parent_info} \n Special: {special_state_info}')
                parent_info['children'] += "\n" + special_state_info['children']

    for state_id, state_info in states.items():
        children_lines = state_info['children'].split('\n')
        repeat = children_lines.count('')
        for i in range(repeat):
            children_lines.remove('')

        states[state_id]['children'] = ''
        for child in children_lines:
            states[state_id]['children'] += child + '\n'

    toRemove = []

    for transition in transitions:
        print(transition['id'])
        if points.get(transition['id']) is None:
            toRemove.append(transition)

    for transition in toRemove:
        transitions.remove(transition)

    # Draw states
    for state_id, state_info in states.items():
        x, y = state_info['x'], state_info['y']
        rect_width = state_info['width']
        rect_height = state_info['height']
        caption = state_info['caption']
        font_shift = state_info['fontShift']
        color = state_info['color']
        print(rect_width)
        print(rect_height)
        dwg.add(dwg.rect(insert=(x, y), size=(rect_width, rect_height),
                         rx=10, ry=10, fill=color, stroke='black'))
        if caption['x'] != 0 and caption['y'] != 0:
            dwg.add(
                dwg.text(state_info['name'], insert=(caption['x']+caption['width']/2, caption['y']+font_shift), text_anchor='middle', font_size='11px',
                         font_family='Arial'))
        dwg.add(dwg.line(start=(x, y+font_shift+2), end=(x + rect_width, y+font_shift+2),
                         stroke='black'))
        if state_info['children']:
            children_lines = state_info['children'].split('\n')
            children_lines.reverse()
            for i, line in enumerate(children_lines):
                dwg.add(dwg.text(line, insert=(x+2, y + font_shift * (i+1.3)), text_anchor='start',
                                 font_size='10px',
                                 font_family='Arial'))

    # Draw transitions
    for transition in transitions:
        print(transition['id'])
        pointsOfTransition = points.get(transition['id'])
        previous = None
        for i in range(len(pointsOfTransition)):
            if previous is None:
                previous = pointsOfTransition[i]
                continue
            actualPoint = pointsOfTransition[i]
            if i == len(pointsOfTransition) - 1:
                dwg.add(dwg.line(start=(previous.get('x'), previous.get('y')),
                                 end=(actualPoint.get('x'), actualPoint.get('y')), stroke='black',
                                 marker_end=arrow_marker.get_funciri()))
                break
            dwg.add(
                dwg.line(start=(previous.get('x'), previous.get('y')), end=(actualPoint.get('x'), actualPoint.get('y')),
                         stroke='black'))
            previous = actualPoint
        dwg.add(dwg.text(transition['name'], insert=(transition['x']+120, transition['y']+47), text_anchor='middle', font_size='10px',
                         font_family='Arial'))

    # Save the SVG file
    dwg.save()
    print('SVG file ' + output_file + ' created successfully.')


def main():
    xml_file = 'sumxmls/simple_state.xml'
    output_file = 'simple_state.svg'
    parse(xml_file, output_file)


if __name__ == "__main__":
    main()
