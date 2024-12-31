(() => {
  'use strict'  
  // Graphs
  // Récupération des données depuis des balises data-* injectées dans le HTML
  const labels = JSON.parse(document.getElementById('charts-data-labels_eco').dataset.labels);
  const consoElec = JSON.parse(document.getElementById('charts-data-consoelec_eco').dataset.consoelec);
  const consoEau = JSON.parse(document.getElementById('charts-data-consoeau_eco').dataset.consoeau);
  const consoDechets = JSON.parse(document.getElementById('charts-data-consodechets_eco').dataset.consodechets);
  const consoCopro = JSON.parse(document.getElementById('charts-data-consocopro_eco').dataset.consocopro);

  const ecoElec = JSON.parse(document.getElementById('charts-data-ecoelec').dataset.consoelec);
  const ecoEau = JSON.parse(document.getElementById('charts-data-ecoconsoeau').dataset.consoeau);
  const ecoDechets = JSON.parse(document.getElementById('charts-data-ecoconsodechets').dataset.consodechets);
  const ecoCopro = JSON.parse(document.getElementById('charts-data-ecoconsocopro').dataset.consocopro);

  console.log({ labels, consoElec, consoEau, consoDechets, consoCopro, ecoElec, ecoEau, ecoDechets, ecoCopro });
  // const ctx = document.getElementById('myChart')
  // eslint-disable-next-line no-unused-vars
  const createChart = (ctx, label, data, labelEco, dataEco) => { //Fonction de création de graph
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
        },{
          label: labelEco, //montantS sans ecorep 
          data: dataEco,
          lineTension: 0,
          backgroundColor: 'transparent',
          borderColor: '#17ad21',
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
createChart(document.getElementById('chartElec_eco'), "Montant dépensé en électricité avec ECOREP", consoElec, "Montant dépensé en électricité SANS ECOREP",ecoElec); //graphe associé à l'élément dont l'id est "chartElec
createChart(document.getElementById('chartEau_eco'), "Montant dépensé en eau avec ECOREP", consoEau,"Montant dépensé en eau SANS ECOREP", ecoEau);
createChart(document.getElementById('chartDechets_eco'), "Montant dépensé en déchets avec ECOREP", consoDechets, "Montant dépensé en déchets SANS ECOREP", ecoDechets);
createChart(document.getElementById('chartCopro_eco'), "Montant dépensé en charges de copropriété avec ECOREP", consoCopro,"Montant dépensé en charge de copropriété SANS ECOREP", ecoCopro);
})();

