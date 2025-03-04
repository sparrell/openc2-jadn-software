"""
Translate each schema file in Source directory to multiple formats in Out2 directory
"""
import fire
import jadn
import os
import shutil

SCHEMA_DIR = 'Schemas'
OUTPUT_DIR = 'Out'


def translate(filename: str, sdir: str, odir: str) -> None:
    if not os.path.isfile(p := os.path.join(sdir, filename)):
        return
    with open(p, encoding='utf8') as fp:
        schema = jadn.load_any(fp)
    print(f'{filename}:\n' + '\n'.join([f'{k:>15}: {v}' for k, v in jadn.analyze(jadn.check(schema)).items()]))

    fn, ext = os.path.splitext(filename)
    jadn.dump(schema, os.path.join(odir, fn + '.jadn'))
    jadn.dump(jadn.transform.unfold_extensions(jadn.transform.strip_comments(schema)),
              os.path.join(odir, fn + '-core.jadn'))
    for form in ('graphviz', 'plantuml'):
        ext = {'graphviz': 'dot', 'plantuml': 'puml'}[form]
        for detail in ('conceptual', 'logical', 'information'):
            for attrs in (False, True):
                f = os.path.join(odir, fn + f'_{detail[0]}{"a" if attrs else ""}.{ext}')
                jadn.convert.diagram_dump(schema, f, style={'format': form, 'detail': detail, 'attributes': attrs})
    jadn.convert.jidl_dump(schema, os.path.join(odir, fn + '.jidl'), style={'desc': 50})
    jadn.convert.html_dump(schema, os.path.join(odir, fn + '.html'))
    jadn.convert.markdown_dump(schema, os.path.join(odir, fn + '.md'))
    jadn.translate.json_schema_dump(schema, os.path.join(odir, fn + '.json'))


def main(schema_dir: str = SCHEMA_DIR, output_dir: str = OUTPUT_DIR) -> None:
    print(f'Installed JADN version: {jadn.__version__}\n')
    css_dir = os.path.join(output_dir, 'css')
    os.makedirs(css_dir, exist_ok=True)
    shutil.copy(os.path.join(jadn.data_dir(), 'dtheme.css'), css_dir)
    for f in os.listdir(schema_dir):
        translate(f, schema_dir, output_dir)


if __name__ == '__main__':
    fire.Fire(main)
