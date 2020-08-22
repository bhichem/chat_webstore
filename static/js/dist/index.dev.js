"use strict";

var first_chat = true;
var socket = io.connect('http://' + document.domain + ':' + location.port);
var productTemplate = $('#product-template');
var msgReceivedTemplate = $('#msg-received-template');
var msgSentTemplate = $('#msg-sent-template');

function processMessage() {
  var message = $('#message').val();
  var userId = $('#user-id').val();
  var msgElement = msgSentTemplate.clone();
  displayMessage(message, msgElement);
  socket.emit('my event', {
    user_id: userId,
    message: message
  });
  $('#message').val('').focus();
}

function setProducts(products, productTemplate) {
  $('#products-container').empty();
  $.each(products, function (index, product) {
    var productElement = productTemplate.clone();
    productElement.removeAttr('id');
    productElement.find('img').attr('src', 'static/imgs/' + product['image']);
    productElement.find('.card-title a').text(product['title']);
    productElement.find('.card-text').text(product['description']);
    productElement.find('h5').text(product['price']);
    $('#products-container').append(productElement);
  });
}

function displayMessage(message, msgElement) {
  msgElement.removeAttr('id').removeClass('hidden');
  msgElement.find('p').text(message);
  $('#chat-container').append(msgElement);
  document.getElementById('chat-container').scrollTop = 99999999;
}

$(document).ready(function () {
  $('#btn-chat').click(function (e) {
    e.preventDefault();
    processMessage();
  });
  socket.on('connect', function () {
    socket.emit('my event', {
      data: 'User Connected'
    });
  });
  socket.on('my response', function (msg) {
    if (msg.response) {
      var response = msg.response;
      var msgElment = msgReceivedTemplate.clone();
      displayMessage(response, msgElment);
      setProducts(msg.products, productTemplate);
    }
  });
  $(window).keydown(function (event) {
    if (event.keyCode === 13) {
      if ($("#message").is(":focus")) {
        event.preventDefault();
        processMessage();
        return false;
      }
    }
  });
  $('.togglechat-btn').click(function () {
    var btnText = $(this).text() == 'Chat' ? 'Close' : 'Chat';
    $(this).text(btnText);
    var user_name = $('#user-name').val();
    $('#my-form').toggleClass('show-form');

    if ($('#my-form').hasClass('show-form') && first_chat) {
      var message = 'Hello ' + user_name + ' what product are you looking for?';
      var msgElement = msgReceivedTemplate.clone();
      displayMessage(message, msgElement);
      first_chat = false;
    }
  });
});