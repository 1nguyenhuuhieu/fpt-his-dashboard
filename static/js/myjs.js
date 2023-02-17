const dateQuery = document.getElementById("dateQuery");

const yesterdayLink = document.getElementById("yesterdayLink");
const todayLink = document.getElementById("todayLink");
const toDayString = dateQuery.value;


todayLink.href = todayURL;
let dateYesterday = new Date(toDayString);
dateYesterday.setDate(dateYesterday.getDate() - 1);
stringDate = dateYesterday.toISOString().split('T')[0];
yesterdayLink.href = window.location.origin + urlGenerator+ stringDate;

const dateQueryLink = document.getElementById("dateQueryLink");
dateQuery.addEventListener('change', function(){
    dateQueryFunction(urlGenerator)
} );

function dateQueryFunction(urlGenerator) {
    dateQueryLink.href = window.location.origin + urlGenerator + dateQuery.value;
    dateQueryLink.click()
}
