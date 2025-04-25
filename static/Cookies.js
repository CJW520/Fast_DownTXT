
//设置cookie，name为名称，value为值，expires为过期日，path为路径，domain为域名，secure为加密
function setCookie(name, value, expires, path, domain, secure) {
    var today = new Date();
    today.setTime(today.getTime());
    if (expires) {
        expires = expires * 1000 * 60 * 60 * 24; //计算cookie的过期毫秒数
    }
    //计算cookie的过期日期
    var expires_date = new Date(today.getTime() + (expires));
    //构造并保存cookie字符串
    document.cookie = name + '=' + escape(value) +
        ((expires) ? ';expires=' + expires_date.toGMTString() : '') + //expires.toGMTString()
        ((path) ? ';path=' + path : '') +
        ((domain) ? ';domain=' + domain : '') +
        ((secure) ? ';secure' : '');

}


//获取cookie，参数name指定要获取的cookie的名称
function getCookie(name) {
    var start = document.cookie.indexOf(name + "="); //得到cookie字符串中的名称
    var len = start + name.length + 1; //得到从起始位置到结束cookie位置的长度
    //如果起始没有值且name不存在于cookie字符串中，则返回null
    if ((!start) && (name != document.cookie.substring(0, name.length))) {
        return null;
    }
    if (start == -1) return null; //如果起始位置为-1也为null
    var end = document.cookie.indexOf(';', len); //获取cookie尾部位置
    if (end == -1) end = document.cookie.length; //计算cookie尾部长度
    return unescape(document.cookie.substring(len, end)); //获取cookie值
}