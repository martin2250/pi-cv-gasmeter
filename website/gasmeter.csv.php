<?php
header('Content-Type: text/csv');
header("Cache-Control: no-cache, must-revalidate");
header("Expires: Sat, 26 Jul 1997 05:00:00 GMT");

/*ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);*/

$dmonth = date("n");
$dyear = date("Y");

$months = $_GET['months'];
$years = $_GET['years'];

$monthe = $_GET['monthe'];
$yeare = $_GET['yeare'];

if(!isset($months) || intval($months) > 12 || intval($months) < 0)
{
	$months = $dmonth;
}

if(!isset($monthe) || intval($monthe) > 12 || intval($monthe) < 0)
{
	$monthe = $dmonth;
}

if(!isset($years) || intval($years) < 2000)
{
	$years = $dyear;
}

if(!isset($yeare) || intval($yeare) < 2000)
{
	$yeare = $dyear;
}

$months = intval($months);
$years = intval($years);
$monthe = intval($monthe);
$yeare = intval($yeare);


header('Content-Disposition: attachment; filename="Zaehlestand-' . $months . '.' . $years . '-' . $monthe . '.' . $yeare . '.csv"');

$servername = "localhost";
$username = "";
$password = "";
$database = "";

$conn = new mysqli($servername, $username, $password, $database);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$query = "SELECT * FROM `Gas` WHERE DATE(`Zeit`) >= '%d-%d-1' AND DATE(`Zeit`) < DATE_ADD('%d-%d-1',INTERVAL 1 MONTH) ORDER BY `Gas`.`Zeit` ASC";
$query = sprintf($query, $years, $months, $yeare, $monthe);
$result = $conn->query($query);

while($row = $result->fetch_assoc())
{
	echo $row["Zeit"] . ";" . $row["Zaehlerstand"] . "\n";
}

$conn->close();
?>
