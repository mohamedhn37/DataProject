import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def process_data(df, treatment, graph_type):
    """
    Applique un traitement sur les données et génère un graphique.
    """
    table = None
    img = io.BytesIO()

    plt.figure(figsize=(10, 5))

    if treatment == "flight_phase":
        table = df['Flight Phase'].value_counts().to_frame().reset_index()
        table.columns = ["Phase de vol", "Nombre d'événements"]
        sns.barplot(x=table["Phase de vol"], y=table["Nombre d'événements"])

    elif treatment == "top_events":
        table = df['Event Description'].value_counts().head(10).to_frame().reset_index()
        table.columns = ["Événement", "Nombre"]
        sns.barplot(y=table["Événement"], x=table["Nombre"], palette="coolwarm")

    elif treatment == "ac_type":
        table = df['A/C Type'].value_counts().head(10).to_frame().reset_index()
        table.columns = ["Type d'Avion", "Nombre"]
        sns.barplot(y=table["Type d'Avion"], x=table["Nombre"], palette="viridis")

    elif treatment == "routes":
        table = df.groupby(['From', 'To']).size().reset_index(name="Nombre d'Événements")
        table = table.sort_values(by="Nombre d'Événements", ascending=False).head(10)
        sns.barplot(y=table["From"] + " → " + table["To"], x=table["Nombre d'Événements"], palette="magma")

    elif treatment == "severity":
        table = df['Severity Class'].value_counts().to_frame().reset_index()
        table.columns = ["Classe de Sévérité", "Nombre"]
        sns.barplot(x=table["Classe de Sévérité"], y=table["Nombre"], palette="magma")

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return table.to_html(classes='table table-striped'), f"data:image/png;base64,{plot_url}"
