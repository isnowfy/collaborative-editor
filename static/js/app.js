var dmp = new diff_match_patch();
var down = false;
var comet_timestamp;
var cur_diff = Array();
function diff(text1, text2){
    var d = dmp.diff_main(text1, text2);
    var ret = Array();
    var now = 0;
    for(var i=0; i<d.length; ++i){
        if(d[i][0] == 0)
            now += d[i][1].length;
        if(d[i][0] == 1)
            ret.push([1, now, d[i][1]]);
        if(d[i][0] == -1){
            ret.push([0, now, d[i][1].length]);
            now += d[i][1].length
        }
    }
    return ret;
}
function patch_final(cursor){
    $('#text').val(text);
    curtxt = text;
    $('#text').get(0).setSelectionRange(cursor, cursor);

}
function patch(txt_patch){
    var cursor = $('#text').get(0).selectionStart;
    var txt = text;
    for(var i=0;i<txt_patch.length;++i){
        var tmp = txt_patch[i];
        if(tmp[0] == 1)
            txt = txt.substring(0, tmp[1])+tmp[2]+txt.substring(tmp[1]);
        if(tmp[0] == 0)
            txt = txt.substring(0, tmp[1])+txt.substring(tmp[1]+tmp[2]);
    }
    var tmp = $('#text').val();
    //$('#text').val(txt);
    text = txt;
    //curtxt = txt;
    //cursor = get_cursor(cursor);
    var l = tmp.length;
    if(l != cursor){
        var match = dmp.match_main(txt, tmp.substring(cursor, cursor+20), cursor);
        if(match>=0)
            cursor = match;
        else{
            var ll = cursor;
            if(ll>20)
                ll = 20;
            match = dmp.match_main(txt, tmp.substring(cursor-ll, cursor), cursor);
            if(match>=0)
                cursor = match+ll;
        }
    }
    else
        cursor = txt.length;
    return cursor;
}
function get_cursor(cursor){
    for(var i=cur_diff.length-1;i>=0;--i){
        var tmp = cur_diff[i];
        if(tmp[0] == 1)
            if(tmp[1] <= cursor){
                if(tmp[1]+tmp[2].length >= cursor)
                    cursor = tmp[1];
                else
                    cursor -= tmp[2].length;
            }
        if(tmp[0] == 0)
            if(tmp[1] <= cursor)
                cursor += tmp[2];
    }
    for(var i=0;i<all_patch.length;++i){
        var tmp = all_patch[i];
        if(tmp[0] == 1)
            if(tmp[1] <= cursor)
                cursor += tmp[2].length;
        if(tmp[0] == 0)
            if(tmp[1] <= cursor){
                if(tmp[1]+tmp[2] <= cursor)
                    cursor -= tmp[2];
                else
                    cursor = tmp[1];
            }
    }
    return cursor;
}
function init(){
    first_get();
    $('#text').keydown(function(){down=true;});
    $('#text').keyup(function(){send();});
}
function first_get(){
    $.ajax({
        type: 'POST',
        data: {doc:doc},
        dataType: 'json',
        url: '/first',
        success: function(msg){
            text = msg.txt;
            timestamp = msg.timestamp;
            comet_timestamp = timestamp;
            curtxt = text;
            $('#text').val(text);
            comet();
        }
    });
}
function handle_diff(tmp_diff){
    var ret = [tmp_diff[0]];
    for(var i=1;i<tmp_diff.length;++i){
        for(var j=0;j<i;++j){
            var tmp = tmp_diff[i];
            if(tmp_diff[j][0] == 1)
                if(tmp_diff[j][1] <= tmp[1])
                    tmp[1] += tmp_diff[j][2].length;
            if(tmp_diff[j][0] == 0)
                if(tmp_diff[j][1] <= tmp[1])
                    tmp[1] -= tmp_diff[j][2];
        }
        ret.concat(tmp);
    }
    return ret;
}
function send(){
    down = false;
    var tmp_diff = diff(curtxt, $('#text').val());
    if(tmp_diff.length == 0)
        return;
    curtxt = $('#text').val();
    cur_diff = cur_diff.concat(handle_diff(tmp_diff))
    version += 1;
    $.ajax({
        type: 'POST',
        data: {doc:doc, user:user, parent:timestamp, version:version, diff:JSON.stringify(tmp_diff), password:password},
        dataType: 'json',
        url: '/send',
        success: function(msg){
        }
    });
}
function comet(){
    $.ajax({
        type: 'POST',
        data: {doc:doc, user:user, parent:comet_timestamp},
        dataType: 'json',
        url: '/handle',
        success: function(msg){
            var now_timestamp = msg.timestamp;
            var now_version = msg.version;
            comet_timestamp = now_timestamp;
            all_patch = all_patch.concat(msg.patch);
            var cursor = patch(msg.patch);
            if(now_version>=version && !down){
                version = 0;
                timestamp = now_timestamp;
                patch_final(cursor);
                all_patch = Array();
                cur_diff = Array();
            }
            comet();
        },
        error: function(msg){
            comet();
        }
    });
}
