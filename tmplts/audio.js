elaudios = document.getElementsByTagName('audio');
for (i = 0; i < elaudios.length; i ++) {
  let elaudio = elaudios[i];
	elaudio.removeAttribute('controls')
  let btn = document.createElement('button');
  btn.setAttribute('type','button')
  btn.innerHTML = 'Play';
  elaudio.parentNode.insertBefore(btn, elaudio);
  btn.onclick = function(){
    for (i = 0; i < elaudios.length; i ++) {
  		let elaudio = elaudios[i];
      elaudio.pause();
      elaudio.fastSeek(0);
    }
    elaudio.play();
  }
}

