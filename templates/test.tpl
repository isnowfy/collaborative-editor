% include header
<div style="text-align:center">
<p><a href="/preview/{{doc}}/">preview</a>
and you can copy the code <strong>&lt;script src="http://doit.sinaapp.com/show/{{doc}}.js"&gt;&lt;/script&gt;</strong> to share</p>
</div>
<div class="stack">
<textarea id="text" style="width:100%;height:100%"></textarea>
<script>
var user='{{user}}';
var timestamp={{timestamp}};
var doc='{{doc}}';
var text;
var curtxt;
var version=0;
var all_patch=Array();
var password='{{password}}';
init();
</script>
</div>
<div style="position:absolute;bottom:20px;right:0;left:0;text-align:center;">
you can put password to avoid other's editing
<form action="/password" method="post">
<input type="hidden" name="password" value="{{password}}">
<input type="hidden" name="doc" value="{{doc}}">
<input type="text" name="newpassword" placeholder="password"/>
<input type="submit" name="submit" value="add password">
</form>
</div>
% include footer
