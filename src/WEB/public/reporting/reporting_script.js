// Initialisation des filtres
function initFilters() {
  const strategyFilter = document.getElementById('strategy-filter');
  const assetFilter = document.getElementById('asset-filter');
  const timeframeFilter = document.getElementById('timeframe-filter');
}

// Mise à jour des KPIs
function updateKPIs() {
  document.getElementById('total-profit').textContent =1 ;
  document.getElementById('win-rate').textContent = 1;
  document.getElementById('profit-factor').textContent =1 ;
  document.getElementById('max-drawdown').textContent = 1;
}

const switchBtn = document.querySelector('#switch-tables-btn');
switchBtn.addEventListener('click', () => {
  const ordersTable = document.querySelector('.orders-table-container');
  const positionsTable = document.querySelector('.positions-table-container');
  if (positionsTable.classList.contains('hidden')) {positionsTable.classList.remove('hidden');
    ordersTable.classList.add('hidden');
    switchBtn.textContent = 'Voir les Ordres';} 
  else {ordersTable.classList.remove('hidden');
    positionsTable.classList.add('hidden');
    switchBtn.textContent = 'Voir les Positions';}});

// Mise à jour du tableau des ordres
function updateOrdersTable(orders) {
  const tableBody = document.querySelector('#orders-table tbody');
  tableBody.innerHTML = '';
  orders.forEach(order => {
      const row = document.createElement('tr');
      row.innerHTML = `
      <td>${order.Order_ID}</td>
      <td>${order.Grid_ID}</td>
      <td>${order.OrderTime}</td>
      <td>${order.OrderType}</td>
      <td>${order.OrderPrice}</td>
      <td>${order.OrderQuantity}</td>
      <td>${order.OrderLeverage}x</td>
      <td>${order.OrderTakeProfit}</td>
      <td>${order.OrderStopLoss}</td>
      <td>${order.OrderStatus}</td>
      <td>${order.OrderJustif}</td>`;
      tableBody.appendChild(row);
  });
}

// Mise à jour du tableau des positions
function updatePositionsTable(positions) {
  const tableBody = document.querySelector('#positions-table tbody');
  tableBody.innerHTML = '';
  positions.forEach(position => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${position.Position_ID}</td>
        <td>${position.OrderId}</td>
        <td>${position.Grid_ID}</td>
        <td>${position.EventData_Time}</td>
        <td>${position.BackTest_ID}</td>
        <td>${position.EventCode}</td>
        <td>${position.PositionQty}</td>
        <td>${position.PositionEntryPrice}</td>
        <td>${position.PositionClosePrice}</td>
        <td>${position.ActualPrice}</td>
        <td>${position.CryptoBalance}</td>
        <td>${position.MoneyBalance}</td>`;
      tableBody.appendChild(row);
  });
}

// Gestion du changement de vue
function setupViewSwitcher() {
  const viewButtons = document.querySelectorAll('.view-btn');
  viewButtons.forEach(button => {
      button.addEventListener('click', () => {
          document.querySelectorAll('.view-btn').forEach(btn => btn.classList.remove('active'));
          document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
          button.classList.add('active');
          const viewId = button.getAttribute('data-view');
          document.getElementById(viewId).classList.add('active');
      });
  });
}

async function fetch_data(){
  try {
    const data = await fetch('/ReportingData')
    const Tableau = await data.json();
    return Tableau}
  catch (err) {
      console.log(err)}};

async function fetch_curve(data_file,position_file) {
  try{
  const curve = await fetch(`/GetCurve/${data_file}.csv/${position_file}.csv`)
  const json_curve = await curve.json();
  console.log(json_curve);
  document.getElementById("svg-container").innerHTML = json_curve.equity_curve;}
  catch(error){
      console.error("Error loading SVG:", error);
      document.getElementById("svg-container").innerText = "Failed to load chart.";}};

// Initialisation de l'application
async function initApp() {
  data = await fetch_data();
  wich_file = await fetch('/get_data/datafile')
  console.log(wich_file)
  which_file = await wich_file.json()
  fetch_curve(which_file.response,'position');
  setupViewSwitcher();
  console.log(data)
  // initFilters();
  updateKPIs();
  updateOrdersTable(data.data.orders);
  updatePositionsTable(data.data.positions);
}
// Lancement de l'application lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', initApp);