def creerPage(donnees):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
        <script type="text/javascript">
            google.charts.load('current', {{'packages':['corechart']}});
            google.charts.setOnLoadCallback(drawChart);
            function drawChart() {{
                var data = google.visualization.arrayToDataTable({donnees});
                var options = {{
                    title: 'Synthèse des Factures'
                }};
                var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                chart.draw(data, options);
            }}
        </script>
    </head>
    <body>
        <div id="piechart" style="width: 900px; height: 500px;"></div>
    </body>
    </html>
    """
    # Sauvegarde dans un fichier HTML
    with open("synthese_camembert.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    
# def creerPage(liste : list) :
#     file = open("camembert.html")
#     file.write("<html>")
#     file.write("<head>")
#     file.write("<!--Load the AJAX API-->")
#     file.write("<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>")
#     file.write("<script type="text/javascript">")

#       # Load the Visualization API and the corechart package.
#     file.write("  google.charts.load('current', {'packages':['corechart']});")

#       # Set a callback to run when the Google Visualization API is loaded.
#     file.write("  google.charts.setOnLoadCallback(drawChart);")

#       # Callback that creates and populates a data table,
#       # instantiates the pie chart, passes in the data and
#       # draws it.
#     file.write("  function drawChart() {")

#         # Create the data table.
#     file.write("    var data = new google.visualization.DataTable();")
#     file.write("    data.addColumn('string', 'Topping');")
#     file.write("    data.addColumn('number', 'Slices');")
#     file.write("    data.addRows([")
#     for i in liste :
#         file.write(f"{      i},\n")
#     file.write("    ]);")

#         # Set chart options
#     file.write("        var options = {'title':'How Much Pizza I Ate Last Night',")
#     file.write("                   'width':400,")
#     file.write("                   'height':300};")

#         # Instantiate and draw our chart, passing in some options.
#     file.write("    var chart = new google.visualization.PieChart(document.getElementById('chart_div'));")
#     file.write("    chart.draw(data, options);")
#     file.write("  }")
#     file.write("</script>")
#     file.write("</head>")

#     file.write("<body>")
#     file.write("<!--Div that will hold the pie chart-->")
#     file.write("<div id="chart_div"></div>")
#     file.write("</body>")
#     file.write("</html>)")