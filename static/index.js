document.addEventListener('DOMContentLoaded', function(){
			var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
			socket.on('connect', function(){
				document.querySelector('#reply').onclick = function(){
					const message = document.querySelector('#comment_box').value;
					socket.emit('submit', message, "{{ room }}");
					document.querySelector('#comment_box').value = "";
				}
			});
			
			socket.on('send reply', function(data) {
				var new_message = document.createElement("li");
				new_message.appendChild(document.createTextNode(data));
				
				document.querySelector('#chat_window').appendChild(new_message);
			});
			
			document.querySelector('#rooms').onchange = function(){
				document.querySelector('#chat_room_title').innerHTML = document.querySelector('#rooms').value;
			
			}
		});