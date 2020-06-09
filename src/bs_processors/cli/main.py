import click



@click.group()
def main():
    pass


@click.option("--output-dir", prompt="output directory", help="the input directory")
@click.option("--input-dir", prompt="input directory", help="the input directory")
@click.option("--processor", prompt="processor file", help="the processor file")
@main.command()
def p_dir(input_dir, output_dir, processor):
    click.echo(f"hello {input_dir} from main")
