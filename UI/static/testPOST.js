lesson_bsids = ['383402', '383403', '382013'];

function loadjq(){
  x = document.createElement('script');
  x.src="https://code.jquery.com/jquery-3.2.1.js";
  document.getElementsByTagName('head')[0].appendChild(x);
}

function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;

  // While there remain elements to shuffle...
  while (0 !== currentIndex) {

    // Pick a remaining element...
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex -= 1;

    // And swap it with the current element.
    temporaryValue = array[currentIndex];
    array[currentIndex] = array[randomIndex];
    array[randomIndex] = temporaryValue;
  }

  return array;
}

function randint(max_num){
  return 1 + Math.floor(Math.random() * max_num);
}

function randomdata(){
  return {bsid: lesson_bsids[randint(lesson_bsids.length)-1],
    now_number: randint(40)};
}

function run(){
  loadjq();
  function sendData() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      loadjq();
      alert(this.responseText);
    }

    var data = [];
    shuffle(lesson_bsids).slice(0, randint(lesson_bsids.length)).forEach(function(bsid){
      data.push({bsid: bsid, now_number: randint(40)});
    });
    var url = "";
    data.forEach(function(e){
        url += e.bsid + "=" + e.now_number + "&";
    });
    url = url.trim("&");
    xhttp.open("POST", "http://localhost/myphp/xuanke/getPOST.php", true);
    xhttp.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhttp.send(url);
  };
  sendData();
}

