from flask import Flask, render_template, request
import mysql
import mysql.connector

def connect():
    con = mysql.connector.connect(host='piratesdragon.mysql.pythonanywhere-services.com',
                                  database='piratesdragon$meta_corpus',
                                  user="piratesdragon",
                                  password='15091998mM')


    return con

app = Flask(__name__)


def get_source_options():
    con = connect()
    cur = con.cursor()

    cur.execute("SELECT DISTINCT source FROM metaphors WHERE source is not NULL AND source != '?' AND source != 'nan'")
    source_options = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT DISTINCT target FROM metaphors WHERE target is not NULL AND target != '?' AND target != 'nan'")
    target_options = [row[0] for row in cur.fetchall()]
    cur.close()
    return source_options, target_options

@app.route("/")
def index():
    con = connect()
    cur = con.cursor()

    source_options, target_options = get_source_options()
    source_options.insert(0, '---')
    target_options.insert(0, '---')

    cur.close()

    return render_template("index.html", source_options=source_options, target_options=target_options)

@app.route("/texts")
def texts():
    con = connect()
    cur = con.cursor()

    text_id = request.args.get('text_id', default=None)
    start_metaphor = request.args.get('start_metaphor', default=None, type=int)
    end_metaphor = request.args.get('end_metaphor', default=None, type=int)
    start_sentence = request.args.get('start_sentence', default=None, type=int)
    end_sentence = request.args.get('end_sentence', default=None, type=int)

    lemma = request.args.get('lemma', default=None)
    source = request.args.get('source', default=None)
    target = request.args.get('target', default=None)
    pos = request.args.get('pos', default=None)

    prev_url = request.referrer

    if text_id is not None:
        cur.execute("SELECT * FROM texts WHERE id_texts = %s", (text_id,))
    else:
        cur.execute("SELECT * FROM texts")

    value = cur.fetchall()

    cur.close()

    return render_template("texts.html", data=value, prev_url=prev_url, start_sentence=start_sentence,
                         end_sentence=end_sentence, start_metaphor=start_metaphor,
                         end_metaphor=end_metaphor, lemma=lemma, source=source, target=target, pos=pos)

@app.route("/search", methods=['GET', 'POST'])
def search():
    con = connect()
    cur = con.cursor()

    if request.method == 'POST':
        search_query = request.form['search_query']
        search_option = request.form['search_option']
        chosen_source = request.form['sourceSelect']
        chosen_target = request.form['targetSelect']
        final_query = ''
        if search_query != '':
            if search_option == 'reg_exp':
                final_query += f"SELECT * FROM metaphors JOIN sentences ON metaphors.sent_id = sentences.id_sentences " \
                               f"JOIN tokens ON metaphors.id_metaphors = tokens.meta_id WHERE metaphors.meta_text REGEXP \'{search_query}\'"
            elif search_option == 'lemma':
                final_query += f"SELECT * FROM metaphors JOIN sentences ON metaphors.sent_id = sentences.id_sentences " \
                               f"JOIN tokens ON metaphors.id_metaphors = tokens.meta_id WHERE tokens.lemma REGEXP \'{search_query}\'"
            else:
                final_query += f"SELECT * FROM metaphors JOIN sentences ON metaphors.sent_id = sentences.id_sentences " \
                               f"JOIN tokens ON metaphors.id_metaphors = tokens.meta_id WHERE metaphors.meta_text = \'{search_query}\'"

            if chosen_source != '---':
                final_query += f' AND source= \'{chosen_source}\''
            if chosen_target != '---':
                final_query += f' AND target= \'{chosen_target}\''
            final_query += ' AND source != \'nan\''
        else:
            final_query += f'SELECT * FROM metaphors JOIN sentences ON metaphors.sent_id = sentences.id_sentences JOIN tokens ON metaphors.id_metaphors = tokens.meta_id'
            if chosen_source != '---':
                final_query += f' WHERE source= \'{chosen_source}\''
                if chosen_target != '---':
                    final_query += f' AND target= \'{chosen_target}\''
            elif chosen_target != '---':
                final_query += f' WHERE target= \'{chosen_target}\''
            else:
                final_query += ' WHERE metaphors.meta_text = 1'

        cur.execute(final_query)
        search_results = cur.fetchall()
        return render_template("search_results.html", data=search_results, query=search_query, chosen_source=chosen_source,
                               chosen_target=chosen_target)

    cur.close()

    return render_template("index.html")

@app.route("/metaphors")
def metaphors():
    con = connect()
    cur = con.cursor()

    cur.execute(f"SELECT * FROM metaphors JOIN sentences ON metaphors.sent_id = sentences.id_sentences " \
                f"JOIN tokens ON metaphors.id_metaphors = tokens.meta_id WHERE source != \'nan\' ORDER BY meta_text ASC")
    value = cur.fetchall()

    cur.close()

    return render_template("metaphors.html", data=value)

# @app.route("/help")
# def help():
#     return render_template("help.html")

if __name__ == "__main__":
    app.run(debug=True)
