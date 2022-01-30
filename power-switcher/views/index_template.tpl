<!DOCTYPE html>
<html>
<head>
    <title>Observatory</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap core CSS -->
    <link href="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet"
          media="screen">
    <link href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css" rel="stylesheet">
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.2/html5shiv.js"></script>
    <script src="http://cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.js"></script>
    <![endif]-->
</head>
<body>
<div class="container">
<h1>Observatory Power Switcher</h1>
<h2> Uptime <span id="uptime"></span></h2>

    <ul class="nav nav-tabs" role="tablist">
        <li role="presentation" class="active"><a href="#switches" aria-controls="switches" role="tab" data-toggle="tab">Switches</a>
        </li>
        <li role="presentation"><a href="#indi" aria-controls="indi" role="tab" data-toggle="tab">INDI</a></li>
    </ul>

    <div class="tab-content">
        <div role="tabpanel" class="tab-pane active" id='switches'>
            <div class="checkbox">
                <label>
                    <input id="mount" type="checkbox" data-toggle="toggle">
                    Mount
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="ccd" type="checkbox" data-toggle="toggle">
                    CCD 
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="spare" type="checkbox" data-toggle="toggle">
                    Spare 12v 
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="heaters" type="checkbox" data-toggle="toggle">
                    Heaters
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="aux" type="checkbox" data-toggle="toggle">
                    Light Panel
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="focuser" type="checkbox" data-toggle="toggle">
                    Focuser
                </label>
            </div>
            <div class="checkbox">
                <label>
                    <input id="weatherstation" type="checkbox" data-toggle="toggle">
                    WeatherStation
                </label>
            </div>
        </div>
        <div role="tabpanel" class="tab-pane" id='indi'>
            <button type="button" id="wakeonlan" data-loading-text="Waking PC..." class="btn btn-primary"
                    autocomplete="off">
                Wake PC
            </button>
        </div>
    </div>
</div>


<!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
<script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
<!-- Include all compiled plugins (below), or include individual files as needed -->
<script src="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/js/bootstrap.min.js"></script>

<script src="https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js"></script>
<script>
    $(document).ready(function () {

      $.get( 'power', function( data ) {
          set_switch_states(data);          
      }).fail(function() {
          alert('failed')
      });
  
      $.get( 'uptime', function( data ) {
          $('#uptime').text(data);
      }).fail(function() {
          alert('failed')
      });

      $('#wakeonlan').on('click', function () {
          var $btn = $(this).button('loading')
          $.get( 'pc/wake', function( wakeresp ) {
            console.log(wakeresp);
            $btn.button('reset')
          });

        })

      $('#switches input[type=checkbox]').change(
        function() {
            if($(this).is(":checked")) {
                $.get( 'power/'+$(this).attr('id')+'/on', function( data ) {
                    console.log(data)
                })
                .fail(function(data) {
                    console.log(data);
                    alert('failed')
                });
            } else {
                $.get( 'power/'+$(this).attr('id')+'/off', function( data ) {
                    console.log(data)
                })
                .fail(function(data) {
                    console.log(data);
                    alert('failed')
                });
            }
        }
        );
    });
    function set_switch_states(json) {
        console.log('setting states');
        $.each(json, function (key, data) {
            console.log(key+data)
            if(data == 'ON') {
                $('#'+key).bootstrapToggle('on');
            }
        })
    }



</script>
</body>
</html>
