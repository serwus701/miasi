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

def get_state_name(elem):
    """ Retrieve the state's name, considering potential translations or alternate formats. """
    return elem.attrib.get('Name', 'Unnamed')
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

    # Parse states and transitions
    for elem in root.iter():
        if 'State' in elem.tag:
            state_id = elem.attrib.get('Id')
            state_name = get_state_name(elem)
            state_x = float(elem.attrib.get('X', 0))
            state_y = float(elem.attrib.get('Y', 0))
            model_children = parse_model_children(elem)
            print(
                f'Parsed state: ID={state_id}, Name={state_name}, X={state_x}, Y={state_y}, ModelChildren={model_children}')
            if state_x == 0 and state_y == 0:
                # print(model_children)
                special_states[state_id] = {'name': state_name, 'children': model_children}
            else:
                states[state_id] = {'name': state_name, 'x': state_x, 'y': state_y, 'children': model_children}
        elif elem.tag == 'Transition2':
            from_state = elem.attrib.get('From')
            to_state = elem.attrib.get('To')
            transition_name = elem.attrib.get('Name', '')
            print(f'Parsed transition: From={from_state}, To={to_state}, Name={transition_name}')
            if from_state and to_state:
                transitions.append({'from': from_state, 'to': to_state, 'name': transition_name})

    # Integrate special states into their parent states
    for special_state_id, special_state_info in special_states.items():
        for parent_id, parent_info in states.items():
            if special_state_info['name'] in parent_info['name']:
                parent_info['children'] += "\n" + special_state_info['children']

    for state_id, state_info in states.items():
        children_lines = state_info['children'].split('\n')
        repeat = children_lines.count('')
        for i in range(repeat):
            children_lines.remove('')

        states[state_id]['children'] = ''
        for child in children_lines:
            states[state_id]['children'] += child + '\n'

    # Draw states
    for state_id, state_info in states.items():
        x, y = state_info['x'], state_info['y']
        rect_width = 150
        rect_height = 70 + 15 * state_info['children'].count('\n')
        dwg.add(dwg.rect(insert=(x - rect_width / 2, y - rect_height / 2), size=(rect_width, rect_height),
                         rx=10, ry=10, fill='#BFEFFF', stroke='black'))
        dwg.add(dwg.text(state_info['name'], insert=(x, y - rect_height / 2 + 15), text_anchor='middle', font_size='12px',
                         font_family='Arial'))
        if state_info['children']:
            children_lines = state_info['children'].split('\n')
            for i, line in enumerate(children_lines):
                dwg.add(dwg.text(line, insert=(x - 70, y - rect_height / 2 + 35 + 15 * i), text_anchor='start', font_size='10px',
                                 font_family='Arial'))

    # Draw transitions
    for transition in transitions:
        from_state = states.get(transition['from'])
        to_state = states.get(transition['to'])
        if from_state and to_state:
            x1, y1 = from_state['x'], from_state['y']
            x2, y2 = to_state['x'], to_state['y']
            dwg.add(dwg.line(start=(x1, y1), end=(x2, y2), stroke='black', marker_end=arrow_marker.get_funciri()))
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            dwg.add(dwg.text(transition['name'], insert=(mid_x, mid_y - 5), text_anchor='middle', font_size='10px',
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
