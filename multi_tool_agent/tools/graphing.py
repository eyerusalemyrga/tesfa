import os
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

def generate_postwar_chart(metrics, title, filename):
    # Ensure values are safe from NoneType errors
    labels = list(metrics.keys())
    values = [v if v is not None else 0.0 for v in metrics.values()]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=['#e74c3c', '#3498db'])
    ax.set_title(title)

    # 1. Sanitize filename (remove spaces if necessary)
    safe_filename = filename.replace(" ", "_")
    
    # 2. Define output directory and ensure it exists
    output_dir = os.path.join(os.getcwd(), "static", "charts")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, safe_filename)

    # 3. Save figure
    fig.savefig(output_path)
    plt.close(fig)

    return f"/static/charts/{safe_filename}"