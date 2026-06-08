import os

with open('panchang_app/templates/kundali.html', 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

new_lines = lines[:77] + [
    '    <div class="kundali-app-content p-3 pb-5" id="kundali-content-wrapper">',
    "        {% include 'kundali_content.html' %}",
    '    </div>'
] + lines[384:]

with open('panchang_app/templates/kundali.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')
