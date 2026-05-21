import os

import polars as pl

INPUT_PATH = "data/processed/transformado.csv"
OUT_TXT = "data/processed/resumen.txt"


def resume_data(
    input_path: str,
    out_txt: str,
) -> None:
    """
    Genera un resumen estadístico global.
    """
    os.makedirs(os.path.dirname(out_txt), exist_ok=True)

    df = pl.read_csv(input_path)

    total_students = df.height

    general_average = df.select(
        pl.col("promedio").mean(),
    ).item()

    min_grade = df.select(
        pl.col("promedio").min(),
    ).item()

    max_grade = df.select(
        pl.col("promedio").max(),
    ).item()

    pass_rate = (
        df.filter(pl.col("categoria").is_in(["Aprobado", "Destacado"])).height
        / total_students
        * 100
    )

    avg_attendace = df.select(
        pl.col("asistencia").mean(),
    ).item()

    count = df.group_by("categoria").len().to_dicts()

    category_count = {d["categoria"]: d["len"] for d in count}

    resume = (
        "Resumen estadístico\n"
        "---------------------\n"
        f"- Total estudiantes procesados: {total_students}.\n"
        f"- Promedio General del curso: {general_average:.2f}.\n"
        f"- Nota Mínima: {min_grade:.2f}.\n"
        f"- Nota Máxima: {max_grade:.2f}.\n"
        f"- Porcentaje de estudiantes aprobados: {pass_rate:.2f}%.\n"
        f"- Conteo categoría Destacado: "
        f"{category_count.get('Destacado', 0)}.\n"
        f"- Conteo categoría Aprobado: {category_count.get('Aprobado', 0)}.\n"
        "- Conteo categoría Reprobado: "
        f"{category_count.get('Reprobado', 0)}.\n"
        f"- Promedio de asistencia del curso: {avg_attendace:.2f}%.\n"
    )

    with open(out_txt, "w") as f:
        f.write(resume)


if __name__ == "__main__":
    resume_data(
        INPUT_PATH,
        OUT_TXT,
    )
