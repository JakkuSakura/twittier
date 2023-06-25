const RequestType = {
    FAVORITERS: 'Favoriters',
    RETWEETERS: 'Retweeters',
    COMMENT: 'TweetDetail',
    QUOTES: 'adaptive'
};

function get_type_by_url(url) {
    if (!url)
        return null;
    for (const t of Object.values(RequestType)) {
        if (url.includes(t)) {
            console.log(url, t, url.includes(t));
            return t;
        }
    }
    return null;
}

function insert_user_action(user_actions, user, action) {
    if (!user_actions[user]) {
        user_actions[user] = new Set();
    }
    user_actions[user].add(action);
}

function get_favorite_users(response, user_actions) {
    let data = JSON.parse(response['content']['text']);
    if ('data' in data) {
        data = data['data'];
    }

    if (!('favoriters_timeline' in data)) {
        return;
    }

    let entries;

    try {
        entries = data['favoriters_timeline']['timeline']['instructions'][0]['entries'];
    } catch (error) {
        return;
    }
    console.log("entries", data['favoriters_timeline'], entries);

    let entry_rt = [];

    for (let i in entries) {
        const entry = entries[i];
        let legacy;

        try {
            legacy = entry['content']['itemContent']['user_results']['result']['legacy'];
        } catch (error) {
            continue;
        }

        entry_rt.push(entry);
        insert_user_action(user_actions, legacy['screen_name'], '喜欢');
    }

    return entry_rt;
}

function get_retweeters(response, user_actions) {
    let data = JSON.parse(response['content']['text']);
    if ('data' in data) {
        data = data['data'];
    }
    if (!('retweeters_timeline' in data)) {
        return;
    }
    let entries;
    try {
        entries = data['retweeters_timeline']['timeline']['instructions']['entries'];
    } catch (e) {
        return;
    }
    const entry_rt = [];
    for (let i in entries) {
        const entry = entries[i];
        try {
            const legacy = entry['content']['itemContent']['user_results']['result']['legacy'];
        } catch (e) {
            continue;
        }
        entry_rt.push(entry);
        insert_user_action(user_actions, legacy['screen_name'], '转推');
    }
    // FIXME: seems to have bugs
    return entry_rt;
}

function get_comments(response, user_actions) {
    let data = JSON.parse(response['content']['text']);
    if ('data' in data) {
        data = data['data'];
    }
    if (!('threaded_conversation_with_injections_v2' in data)) {
        return;
    }
    let entries;
    try {
        entries = data['threaded_conversation_with_injections_v2']['instructions']['entries'];
    } catch (e) {
        return;
    }
    const entry_rt = [];
    for (let i in entries) {
        const entry = entries[i];
        console.log("entry", entry);
        if (!entry['entryId'].startsWith('conversationthread')) {
            continue;
        }
        var legacy;
        try {
            legacy = entry['content']['items']['item']['itemContent']['tweet_results']['result']['core']['user_results']['result']['legacy'];
        } catch (e) {
            continue;
        }
        entry_rt.push(entry);
        insert_user_action(user_actions, legacy['screen_name'], '评论');
    }
    return entry_rt;
}

function get_quotes(response) {
    var data = JSON.parse(response['content']['text']);
    try {
        var tweets = data['globalObjects']['tweets'];
    } catch (KeyError) {
        return;
    }
    var rt = [];
    for (var tweet in Object.values(tweets)) {
        if ('quoted_status_id' in tweet) {
            rt.push(tweet);
        }
    }
    return rt;
}

function distinct_objects(objs) {
    var strs = new Set();
    for (var i in objs) {
        const obj = objs[i];
        strs.add(JSON.stringify(obj, null, 2));
    }
    strs = Array.from(strs);
    strs.sort();
    var output = [];
    for (var i in strs) {
        const str = strs[i];
        output.push(JSON.parse(str));
    }
    return output;
}

function joinString(l, s) {
    if (l instanceof Set) {
        l = Array.from(l)
    }
    var ret = '';
    for (const i in l) {
        const ss = l[i];
        if (i > 0)
            ret += s;
        ret += ss;
    }
    return ret;
}
function compute_dynamic_list(user_actions) {
    var dynamic = [];
    for (var [user, actions] of Object.entries(user_actions)) {
        dynamic.push(`@${user} ${joinString(actions, ' ')}`);
    }
    dynamic.sort();
    return dynamic;
}

function parse_har_content(har) {
    console.log('Har', har)
    var likes = [];
    var retweets = [];
    var comments = [];
    var quotes = [];
    var dynamic = {};

    // assuming har JSON data is already loaded into har variable
    var entries = har['log']['entries'];
    for (var i in entries) {
        const entry = entries[i];
        var url = entry['request']?.['url'];
        var response = entry['response'];
        var req_type = get_type_by_url(url);
        if (!req_type) {
            continue;
        }
        console.log("reqtype", req_type);
        if (req_type === RequestType.FAVORITERS) {
            console.log('Fav', entry)
            var rt = get_favorite_users(response, dynamic);
            if (rt === undefined) {
                continue;
            }
            likes = likes.concat(rt);
        } else if (req_type === RequestType.RETWEETERS) {
            console.log('Ret', entry)

            var rt = get_retweeters(response, dynamic);
            if (rt === undefined) {
                continue;
            }
            retweets.push(rt);
        } else if (req_type === RequestType.COMMENT) {
            console.log('comment', entry)

            var rt = get_comments(response, dynamic);
            if (rt === undefined) {
                continue;
            }
            comments.push(rt);
        } else if (req_type === RequestType.QUOTES) {
            console.log('quotes', entry)

            var rt = get_quotes(response);
            if (rt === undefined) {
                continue;
            }
            quotes.push(rt);
        }
    }

    // likes = distinct_objects(likes);
    // retweets = distinct_objects(retweets);
    // comments = distinct_objects(comments);
    // quotes = distinct_objects(quotes);
    dynamic = compute_dynamic_list(dynamic);

    // assuming you want to dump the results to files
    // var fs = require('fs');
    // fs.writeFileSync('likes.json', JSON.stringify(likes, null, 2));
    // fs.writeFileSync('retweets.json', JSON.stringify(retweets, null, 2));
    // fs.writeFileSync('comments.json', JSON.stringify(comments, null, 2));
    // fs.writeFileSync('quotes.json', JSON.stringify(quotes, null, 2));
    // fs.writeFileSync('dynamic.txt', distinct_objects(dynamic).join('\n'));

    return distinct_objects(dynamic);
}