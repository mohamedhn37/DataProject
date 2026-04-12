import matplotlib
matplotlib.use('Agg')  # Headless backend required for Railway / any server without a display

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

VALID_TREATMENTS = {"flight_phase", "top_events", "ac_type", "routes", "severity", "heatmap"}
VALID_GRAPH_TYPES = {"bar", "line", "scatter", "hist", "box", "heatmap"}

REQUIRED_COLUMNS = {
    "flight_phase": ["Flight Phase"],
    "top_events": ["Event Description"],
    "ac_type": ["A/C Type"],
    "routes": ["From", "To"],
    "severity": ["Severity Class"],
    "heatmap": [],
}

def process_data(df, treatment, graph_type):
    """
    Applies a treatment on the data and generates a chart.
    Returns (html_table, plot_url) or raises ValueError on bad input.
    """
    if treatment not in VALID_TREATMENTS:
        raise ValueError(f"Analyse inconnue : {treatment}")
    if graph_type not in VALID_GRAPH_TYPES:
        raise ValueError(f"Type de graphique inconnu : {graph_type}")

    missing = [c for c in REQUIRED_COLUMNS[treatment] if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le fichier : {', '.join(missing)}")

    table = None
    img = io.BytesIO()

    plt.figure(figsize=(10, 5))

    if treatment == "flight_phase":
        table = df['Flight Phase'].value_counts().to_frame().reset_index()
        table.columns = ["Phase de vol", "Nombre d'événements"]

        if graph_type == "bar":
            sns.barplot(x=table["Phase de vol"], y=table["Nombre d'événements"])
        elif graph_type == "line":
            sns.lineplot(x=table["Phase de vol"], y=table["Nombre d'événements"], marker="o")
        elif graph_type == "scatter":
            sns.scatterplot(x=table["Phase de vol"], y=table["Nombre d'événements"])
        elif graph_type == "hist":
            sns.histplot(table["Nombre d'événements"], bins=10, kde=True)
        elif graph_type == "box":
            sns.boxplot(y=table["Nombre d'événements"])

    elif treatment == "top_events":
        table = df['Event Description'].value_counts().head(10).to_frame().reset_index()
        table.columns = ["Événement", "Nombre"]

        if graph_type == "bar":
            sns.barplot(y=table["Événement"], x=table["Nombre"], palette="coolwarm")
        elif graph_type == "line":
            sns.lineplot(y=table["Événement"], x=table["Nombre"], marker="o")
        elif graph_type == "scatter":
            sns.scatterplot(y=table["Événement"], x=table["Nombre"])
        elif graph_type == "hist":
            sns.histplot(table["Nombre"], bins=10, kde=True)
        elif graph_type == "box":
            sns.boxplot(x=table["Nombre"])

    elif treatment == "ac_type":
        table = df['A/C Type'].value_counts().head(10).to_frame().reset_index()
        table.columns = ["Type d'Avion", "Nombre"]

        if graph_type == "bar":
            sns.barplot(y=table["Type d'Avion"], x=table["Nombre"], palette="viridis")
        elif graph_type == "line":
            sns.lineplot(y=table["Type d'Avion"], x=table["Nombre"], marker="o")
        elif graph_type == "scatter":
            sns.scatterplot(y=table["Type d'Avion"], x=table["Nombre"])
        elif graph_type == "hist":
            sns.histplot(table["Nombre"], bins=10, kde=True)
        elif graph_type == "box":
            sns.boxplot(x=table["Nombre"])

    elif treatment == "routes":
        table = df.groupby(['From', 'To']).size().reset_index(name="Nombre d'Événements")
        table = table.sort_values(by="Nombre d'Événements", ascending=False).head(10)

        if graph_type == "bar":
            sns.barplot(y=table["From"] + " → " + table["To"], x=table["Nombre d'Événements"], palette="magma")
        elif graph_type == "line":
            sns.lineplot(y=table["From"] + " → " + table["To"], x=table["Nombre d'Événements"], marker="o")
        elif graph_type == "scatter":
            sns.scatterplot(y=table["From"] + " → " + table["To"], x=table["Nombre d'Événements"])
        elif graph_type == "hist":
            sns.histplot(table["Nombre d'Événements"], bins=10, kde=True)
        elif graph_type == "box":
            sns.boxplot(x=table["Nombre d'Événements"])

    elif treatment == "severity":
        table = df['Severity Class'].value_counts().to_frame().reset_index()
        table.columns = ["Classe de Sévérité", "Nombre"]

        if graph_type == "bar":
            sns.barplot(x=table["Classe de Sévérité"], y=table["Nombre"], palette="magma")
        elif graph_type == "line":
            sns.lineplot(x=table["Classe de Sévérité"], y=table["Nombre"], marker="o")
        elif graph_type == "scatter":
            sns.scatterplot(x=table["Classe de Sévérité"], y=table["Nombre"])
        elif graph_type == "hist":
            sns.histplot(table["Nombre"], bins=10, kde=True)
        elif graph_type == "box":
            sns.boxplot(x=table["Nombre"])

    elif treatment == "heatmap":
        numeric_df = df.select_dtypes(include='number')
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", linewidths=0.5)
        table = numeric_df.corr().reset_index().rename(columns={"index": ""})

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close('all')  # Free memory — prevents leaks on repeated requests

    return table.to_html(classes='table table-striped'), f"data:image/png;base64,{plot_url}"
