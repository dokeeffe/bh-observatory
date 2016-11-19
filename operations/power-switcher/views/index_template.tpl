<!DOCTYPE html>
<html>
  <head>
    <title>Bootstrap 3 Template</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Bootstrap core CSS -->
    <link href="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <link href="https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css" rel="stylesheet">
    <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="http://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.2/html5shiv.js"></script>
      <script src="http://cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.js"></script>
    <![endif]-->
  </head>
  <body>
    <div id='switches'>
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
           <input id="filterwheel" type="checkbox" data-toggle="toggle">
           FilterWheel
        </label>
        </div>
    </div>


    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="http://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.4/js/bootstrap.min.js"></script>

    <script src="https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js"></script>
    <script>
    $(document).ready(function () {

      $('#switches input[type=checkbox]').change(
        function() {
            if($(this).is(":checked")) {
                $.get( 'http://192.168.1.225:8080/power/'+$(this).attr('id')+'/on', function( data ) {
                }).done(function() {
                    alert('ok');
                })
                .fail(function() {
                    alert('failed')
                });
            } else {
                alert('off');
            }
        }
    );

  });
</script>
  </body>
</html>