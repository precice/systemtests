""" Interactive script to generate tests boilerplate """

from jinja2 import Template
from collections import namedtuple
import re
import os

def generate_test_structure(test_name = None, base_image = None,
        participants = None, tutorial_path = None):

    tmp_files = os.listdir(os.path.join('templates','test_template'))

    # adjust variables for easier reading in template files
    adapters      = [ p.split(':')[0] for p in participants ]
    solvers       = [ a.replace('-adapter','') for a in adapters ]
    participants  = [ p.replace(':','_') for p in participants]
    input_volumes = ['input_' + p  for p in participants]
    precice_base  = '-' + base_image.lower() + '-develop'
    # to pass zip to jinja
    zipped_input = zip(participants, solvers, adapters)


    renders = {t.replace('.jinja', ''): '' for t in tmp_files}
    for tmp_file in tmp_files:
        with open(os.path.join('templates','test_template', tmp_file)) as f:
            tmp = Template(f.read())
            renders[tmp_file.replace('.jinja', '')] = tmp.render(locals())

    otp_dir = os.path.join('tests', "TestCompose_{test}.{base}".format(test =
        test_name, base = base_image))
    os.mkdir(otp_dir)
    for name, render in renders.items():
        with open(os.path.join(otp_dir, name), "w") as otp_f:
            otp_f.write(render)

    print ("Test generated! Find the configuration files in the {otp_dir} directory".\
            format(otp_dir = otp_dir))

def test_name_validator(val):

    if re.match(r'[a-z_\-0-9]+$', val):
        return True
    else:
        return False

def base_image_validator(val):

    if re.match(r'[a-zA-Z0-9.]+$', val):
        return True
    else:
        return False

def participants_validator(val):

    for v in val:
        v = v.split(':')[0]
        if not re.match(r'[\w-]+$', v) or "-adapter" not in v:
            return False

    if (len(set(val)) != len(val)):
        print ("""Error: Duplicate entries in the set. If you want to use one adapter in
        2 participants mark it as for instance openfoam:fluid""")
        return False

    if len(val) < 2:
        print ("""There must be at least two participants!""")
        return False

    return True

def tutorial_dir_validator(val):

    if re.match(r'[\w\-\./]+$', val):
        return True

    return False

def ask_user_input():

    InputHandler = namedtuple("InputHandler", ["msg", "validator"])
    user_inputs_handlers = {\
           'test_name':  InputHandler("Enter new test name. Syntax: participant1-participant2_additionalInfo\n", \
                          test_name_validator),
          'base_image':  InputHandler("Enter new base image for a test. Syntax: BaseImage.feature1.feature2 (e.g 'Ubuntu1604.home')\n",\
                          base_image_validator),
        'participants':  InputHandler("Enter participants for a test. Syntax: participant1, particticipant2 (e.g 'su2-adapter, calculix-adapter')\n",\
                          participants_validator),
        'tutorial_path': InputHandler("Enter tutorials directory which is represented by this test. Syntax: (e.g 'FSI/flap_perp/OpenFOAM-deal.II/')\n",\
                          tutorial_dir_validator)
        }

    user_inputs = {k: None for k in user_inputs_handlers.keys()}

    for k, input_handler in user_inputs_handlers.items():
        while user_inputs[k] is None:

            val = input(input_handler.msg).strip()
            if k == "participants":
                val = [v.strip() for v in val.split(",")]
            if input_handler.validator(val):
                user_inputs[k] = val

    return user_inputs


if __name__ == "__main__":

    user_inputs  = ask_user_input()
    generate_test_structure(**user_inputs)
