% include header
<div style="text-align:center">
<p>you should enter the password to edit</p>
<form action="/password" method="post">
<input type="hidden" name="doc" value="{{doc}}">
<input type="text" name="password" placeholder="password"/>
<input type="submit" name="submit" value="submit">
</form>
</div>
% include footer
