(() => {
  'use strict'  
  // Graphs
  // Récupération des données depuis des balises data-* injectées dans le HTML
  // Chatgpt : comment rendre les variables jinja passées à mon html 
  const labels = JSON.parse(document.getElementById('charts-data-labels').dataset.labels);
  const consoElec = JSON.parse(document.getElementById('charts-data-consoelec').dataset.consoelec);
  const consoEau = JSON.parse(document.getElementById('charts-data-consoeau').dataset.consoeau);
  const consoDechets = JSON.parse(document.getElementById('charts-data-consodechets').dataset.consodechets);
  const consoCopro = JSON.parse(document.getElementById('charts-data-consocopro').dataset.consocopro);
  console.log({ labels, consoElec, consoEau, consoDechets, consoCopro });
  // const ctx = document.getElementById('myChart')
  // eslint-disable-next-line no-unused-vars
  
  const createChart = (ctx, label, data) => { //Fonction de création de graph
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: label, 
          data: data,
          lineTension: 0,
          backgroundColor: 'transparent',
          borderColor: '#007bff',
          borderWidth: 4,
          pointBackgroundColor: '#007bff'
        }]
      },
      options: {
        responsive: true, //redimensionnement du canva
        plugins: {
          legend: {
            display: true,
            labels: {
              font: {
                  size: 12 // Optionnel : Ajustez la taille de la police si nécessaire
              }
            }
          },
          tooltip: {
            boxPadding: 3
          }
        },
        maintainAspectRatio: false
      }
  })
};

//Création des 4 graphes
createChart(document.getElementById('chartElec'), "Électricité (kWh)", consoElec); //graphe associé à l'élément dont l'id est "chartElec
createChart(document.getElementById('chartEau'), "Eau (L)", consoEau);
createChart(document.getElementById('chartDechets'), "Déchets (kg)", consoDechets);
createChart(document.getElementById('chartCopro'), "Copropriété (heures)", consoCopro);
})();

