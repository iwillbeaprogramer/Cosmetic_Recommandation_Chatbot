/**
 * http://usejsdoc.org/
 * uiForChattingClient.js
 * @date 2018-02-22
 * @author saintphs
 */
var botName = '';		// change this to your bot name
var cbTTSEnabled = 'checked';   // TTS Enabled
var cbAutoSend = 'checked';   // Speech Auto Send Enabled
// declare timer variables
var alarm = null;
var callback = null;
var loopback = null;

// 일시 처리
//var currDate = new Date(); 
// 현재 날짜시간 생성
//currDate=dateToYYYYMMDD(currDate);

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip(); 
});

$(function(){
	$('#frmChat').submit(function(e){
	// this function overrides the form's submit() method, allowing us to use AJAX calls to communicate with the ChatScript server
	e.preventDefault();  // Prevent the default submit() method
	var name = $('#txtUser').val();
        if (name == '') {
		alert('Please provide your name.');
		document.getElementById('txtUser').focus();
         }
	var chatLog = $('#responseHolder').html();
	//var youSaid = '<strong>' + name + ':</strong> ' + $('#txtMessage').val() + "<br>\n";
	var youSaid = 	'<li class="right clearfix">'
				+	'    <span class="pull-right">'
				+   '        <i class="fa fa-user" style="font-size:24px;"></i>'
    			+	'    </span>'
    			+	'    <div class="chat-body clearfix" id="chatBodyMessage">'
    			+	'        <div class="header">'
    			+	'            <small class="text-muted">'
    			+	'                <i class="fa fa-clock-o fa-fw"></i>' + dateToYYYYMMDD(new Date()) 
    			+	'            </small>'
    			+	'            <strong class="pull-right primary-font">' + name + '</strong>'
    			+	'        </div>'
    			+	'		 <div style="cborder: 0px solid orange; border-radius: 20px 0px 20px 20px; margin: 5px 0px 5px 10px; padding: 10px; background: #06b79a; color: #fff; float: right; border-top-right-radius: 0;">'
    			+	'        <p>' + $('#txtMessage').val() + '</p>'
    			+	'    	 </div>'
    			+	'    </div>'
    			+	'</li>';

	update(youSaid);
	var data = $(this).serialize();
	sendMessage(data);

	//$('#txtMessage').val('').focus();
	$('#txtMessage').val('').blur();
	
	});

	$('#txtMessage').keypress(function(){
        window.clearInterval(loopback);
        window.clearTimeout(callback);
    });
	// any user typing cancels loopback or callback for this round 
		
});
function sendMessage(data){ //Sends inputs to the ChatScript server, and returns the response-  data - a JSON string of input information
$.ajax({
	url: '/chatapp/call_chatbot',
//	url: '/ark/chatapp/call_chatbot', 
	//dataType : "jsonp",
	dataType: 'text',
	data: data,
    type: 'post',
    success: function(response){
		processResponse(parseCommands(response));
    },
    error: function(xhr, status, error){
		alert('oops? Status = ' + status + ', error message = ' + error + "\nResponse = " + xhr.responseText);
    }
  });
}
function parseCommands(response){ // Response is data from CS server. This processes OOB commands sent from the CS server returning the remaining response w/o oob commands
	//alert('response : '+ response); 
	var len  = response.length;
	var i = -1;
	while (++i < len )
	{
		if (response.charAt(i) == ' ' || response.charAt(i) == '\t') continue; // starting whitespace
		if (response.charAt(i) == '[')  break;	                         // we have an oob starter
		return response;						// there is no oob data 
	}
	if ( i == len) return response; // no starter found
	var user = $('#txtUser').val();
     
	// walk string to find oob data and when ended return rest of string
	var start = 0;
	while (++i < len )
	{
		if (response.charAt(i) == ' ' || response.charAt(i) == ']') // separation
		{
			if (start != 0) // new oob chunk
			{
				var blob = response.slice(start,i);
				start = 0;
				var commandArr = blob.split('=');
				if (commandArr.length == 1) continue;	// failed to split left=right
				var command = commandArr[0]; // left side is command 
				var interval = (commandArr.length > 1) ? commandArr[1].trim() : -1;
// right side is millisecond count
				if (interval == 0)  /* abort timeout item */
				{ 
					switch (command){
						case 'alarm':
							window.clearTimeout(alarm);
							alarm = null;
							break;
						case 'callback':
							window.clearTimeout(callback);
							callback = null;
							break;
						case 'loopback':
							window.clearInterval(loopback);
							loopback = null;
							break;
					}
				}
				else if (interval == -1) interval = -1; // do nothing
				else
				{
					var timeoutmsg = {user: user, send: true, message: '[' + command + ' ]'}; // send naked command if timer goes off 
					switch (command) {
						case 'alarm':
							alarm = setTimeout(function(){sendMessage(timeoutmsg );}, interval);
							break;
						case 'callback':
							callback = setTimeout(function(){sendMessage(timeoutmsg );}, interval);
							break;
						case 'loopback':
							loopback = setInterval(function(){sendMessage(timeoutmsg );}, interval);
							break;
                                                case 'avatar' :
                                                        document.getElementById("avatarImage").src = "images/" + interval;
                                                        break;
					}
				}
			} // end new oob chunk
			if (response.charAt(i) == ']') return response.slice(i + 2); // return rest of string, skipping over space after ] 
		} // end if
		else if (start == 0) start = i;	// begin new text blob
	} // end while
	return response;	// should never get here
 }

function processResponse(response) { // given the final CS text, converts the parsed response from the CS server into HTML code for adding to the response holder div
	//response = replace('\n','<br>\n');
	//var botSaid = '<strong>' + botName + ':</strong> ' + response + "<br>\n";
	//var botSaid = '<strong>' + botName + ':</strong> ' + response + "<br>\n";
	var botSaid = 	'<li class="left clearfix">'
		+	'    <span class="pull-left">'
		+   '        <i class="fa fa-android" style="font-size:24px;"></i>'
		+	'    </span>'
		+	'    <div class="chat-body clearfix" id="chatBodyMessage">'
		+	'        <div class="header">'
		+	'            <strong class="primary-font">' + botName + '</strong>'
		+	'            <small class="pull-right text-muted">'
		+	'                <i class="fa fa-clock-o fa-fw"></i>' + dateToYYYYMMDD(new Date()) +  '</small>'
		+	'        </div>'
		+	'		 <div id="responseMessage" style="border: 0px solid orange; border-radius: 0px 20px 20px 20px;  margin: 5px 10px 5px 0px; padding: 10px; background: #efefef; color: #6f6f6f; float: left; border-top-left-radius: 0;">'
		+	'        <p>' + response + '</p>'
		+	'    	 </div>'
		+	'    </div>'
		+	'</li>';
	
	update(botSaid);
	speak(response);
}

//데이트 포멧 
function dateToYYYYMMDD(date){
    function pad(num) {
        num = num + '';
        return num.length < 2 ? '0' + num : num;
    }
    return date.getFullYear() + '-' + pad(date.getMonth()+1) + '-' + pad(date.getDate()) + ' ' + pad(date.getHours()) + ':' + pad(date.getMinutes()) + ':' + pad(date.getSeconds()); 
}

function update(text){ // text is  HTML code to append to the 'chat log' div. This appends the input text to the response div
	/**
    var el = document.getElementsByClassName("panel-body");
	el.scrollTop = el.scrollHeight - el.scrollTop;

	var chatLog = $('#responseHolder').html();
	$('#responseHolder').html(chatLog + text);
	var rhd = $('#responseHolder');
	var h = rhd.get(0).scrollHeight;
	rhd.scrollTop(h);
    $("#responseHolder").scrollTop(1000);
    */
	var chatLog = $('#responseHolder').html();
	$('#responseHolder').html(chatLog + text);
	//스크롤이 항상 최신 대화가 보이도록 대화메시지 출력후 맨아래로 설정
	var rhd = $('.panel-body');
	var h = rhd.get(0).scrollHeight;
	rhd.scrollTop(h);
	//div 에 focus 주기
	//document.getElementById("responseMessage").scrollIntoView();
}

function restart_chatbot() {
	//alert('Resume the conversation.');
	responseHolder.innerHTML = "";
}

// TTS code taken and modified from here:
// http://stephenwalther.com/archive/2015/01/05/using-html5-speech-recognition-and-text-to-speech
//---------------------------------------------------------------------------------------------------
// say a message
function speak(text, callback) {
    if ( cbTTSEnabled == 'checked' ) {
    	 var msg = new SpeechSynthesisUtterance();
    	 msg.lang = 'ko-KR';
    	 msg.text = text;
    	 speechSynthesis.speak(msg);
    	/**
    	var u = new SpeechSynthesisUtterance();
		// get the voice
    	var voices = window.speechSynthesis.getVoices();
    	var selectedVoice = voices.filter(function (voice) {
	    	return voice.name == 'Google UK English Male';
    	})[0];
    	
    	// create the utterance
		u.text = text;
     	//u.lang = 'en-US';
    	// 2017.06.24 수정
    	//u.lang = 'en-GB';
    	u.lang = 'ko-KR';
    	//u.voice = selectedVoice;  
       	u.rate = .85;  
    	u.pitch = .9;  
    	u.volume = .5;  
 
	u.onend = function () {
        	if (callback) {
            	callback();
        	}
	};
 
    	u.onerror = function (e) {
        	if (callback) {
            		callback(e);
        	}
    	};
 
    	speechSynthesis.speak(u);
    	*/
    }
}
//-----End of TTS Code Block-----------------------------------------------------------------------------
// Continuous Speech recognition code taken and modified from here:
// https://github.com/GoogleChrome/webplatform-samples/tree/master/webspeechdemo
//----------------------------------------------------------------------------------------------------
var final_transcript = '';
var recognizing = false;
var ignore_onend;
var start_timestamp;
if (!('webkitSpeechRecognition' in window)) {
  info.innerHTML = "You need to use Google Chrome to use speech to text functionality. Everything else should still work as expected.";
} else {
  btnMicrophone.style.display = 'inline-block';
  var recognition = new webkitSpeechRecognition();
  //모바일 크롬에서 두번 음성인식 되는 문제 해결을 위해 continuous = false, interimResults = false, maxAlternatives = 1
  //continuous 속성은 마이크 캡쳐를 한 번만 하고 그만 둘 것인지를 정하는데요, 기본은 false로 잡혀있습니다.
  recognition.continuous = false;
  //interimResults 속성은 마이크 캡쳐 중에 브라우저가 단어를 감지할 때마다 결과값을 내보낼 지를 정하는데요, 기본은 역시 false입니다.
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;
  //lang 속성은 감지할 언어를 정합니다. BCP-47를 사용하고, 영어는 en-US, 한국어는 ko-KR, 일본어는 ja-JP 등
  recognition.lang = 'ko-KR';
  
  //webkitSpeechRecognition의 이벤트에는 onstart, onerror, onend, onresult 등이 있습니다.
  //start()로 음성인식을 시작하고, stop()으로 음성인식을 종료
  recognition.onstart = function() {
    recognizing = true;
    info.innerHTML =  " Speak now.";
//    start_img.src = 'images/mic-animate.gif';
  start_img.class = 'fa fa-assistive-listening-systems';
  start_img.style = 'color:red';
  };
  //말소리가 인식되면 onresult 이벤트가 발생, 발생시 받는 데이터의 results의 transcript에는 인식된 말이 저장됩니다.
  recognition.onresult = function(event) {
    var interim_transcript = '';
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
	//----Added this section to integrate with Chat Server submit functionality-----
		processFinalTranscript(final_transcript);
		final_transcript ='';
	//-----------------------------------------------------------------------------
      } else {
        interim_transcript += event.results[i][0].transcript;
      }
    } 
    final_span.innerHTML = final_transcript;
    interim_span.innerHTML = interim_transcript;  
  };
  recognition.onerror = function(event) {
   //alert("microphoneClick event.error : " + event.error);
   if (event.error == 'no-speech') {
      start_img.class = 'fa fa-microphone fa-fw';
      start_img.style = 'color:Snow';
      info.innerHTML = "You did not say anything.";
      ignore_onend = true;
    }
    if (event.error == 'audio-capture') {
      start_img.class = 'fa fa-microphone fa-fw';
      start_img.style = 'color:Snow';
      info.innerHTML = "You need a microphone.";
      ignore_onend = true;
    }
    if (event.error == 'not-allowed') {
      if (event.timeStamp - start_timestamp < 100) {
	//Added more detailed message to unblock access to microphone.
        info.innerHTML = " I am blocked. In Chrome go to settings. Click Advanced Settings at the bottom. Under Privacy click the Content Settings button. Under Media click Manage Exceptions Button. Remove this site from the blocked sites list. ";
      } else {
        info.innerHTML = "You did not click the allow button."
      }
      ignore_onend = true;
    }
  };
  recognition.onend = function() {
    recognizing = false;
    if (ignore_onend) {
      return;
    }
    start_img.class = 'fa fa-microphone fa-fw';
    start_img.style = 'color:Snow';
    if (!final_transcript) {
      info.innerHTML = "Click on the microphone icon and begin speaking.";
      return;
    }
    info.innerHTML = "";
   
  };
}

function microphoneClick(event) {
  //alert("microphoneClick event");
  if (recognizing) {
    recognition.stop();
    return;
  }
  final_transcript = '';
  txtMessage.value = '';
  recognition.start();
  ignore_onend = false;
  final_span.innerHTML = '';
  interim_span.innerHTML = '';
  start_img.class = 'fal fa-microphone-slash';
  start_img.style = 'color:red';
  //start_img.src = 'images/mic-slash.gif';
  info.innerHTML = " Click the Allow button above to enable your microphone.";
  start_timestamp = event.timeStamp;
    
}

function processFinalTranscript(transcript) {
	
	transcript = transcript.trim();	
	txtMessage.value = transcript;
	final_span.innerHTML = '';
   	interim_span.innerHTML = '';
	if (cbAutoSend == 'checked') {
		//alert("txtMessage.value : "+txtMessage.value+"\n");
		$('#frmChat').submit();
	}
	if (recognizing) {
	   recognition.stop();
	}
	
}
//End of Continuous Speech Recognition Block
//----------------------------------------------------------------------------------------------------
