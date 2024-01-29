from flask import Flask, render_template, request, Response, send_file
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from io import BytesIO


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)



class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Fixture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_date = db.Column(db.String(50))
    league_id = db.Column(db.Integer)  
    home_team = db.Column(db.String(50), db.ForeignKey('team.name'), nullable=False)
    away_team = db.Column(db.String(50), db.ForeignKey('team.name'), nullable=False)
    winner = db.Column(db.String(50)) 


    def __repr__(self):
        return f'<Fixture {self.id} - {self.home_team} vs {self.away_team}>'

@app.route('/')
def teams_list():
    # Get all teams
    teams = Team.query.all()

    # Get all fixtures
    fixtures = Fixture.query.all()

    return render_template('teams_list.html', teams=teams, fixtures=fixtures, show_without_fixtures=False)

@app.route('/show_without_fixtures')
def teams_without_fixtures():
    # Get all teams
    teams = Team.query.all()

    # Get teams with fixtures
    teams_with_fixtures = set(fixture.home_team for fixture in Fixture.query.all()) | set(fixture.away_team for fixture in Fixture.query.all())

    # Filter teams without fixtures
    teams_without_fixtures = [team for team in teams if team.name not in teams_with_fixtures]

    return render_template('teams_list.html', teams=teams_without_fixtures, fixtures=[], show_without_fixtures=True)

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('search_query', '').lower()

    # Get all teams
    all_teams = Team.query.all()

    # Get all fixtures
    all_fixtures = Fixture.query.all()

    # Filter teams based on the search query
    matching_teams = [team for team in all_teams if search_query in team.name.lower()]

    # Filter fixtures involving the matching teams
    matching_fixtures = [fixture for fixture in all_fixtures if
                         fixture.home_team in matching_teams or fixture.away_team in matching_teams]

    return render_template('teams_list.html', teams=matching_teams, fixtures=matching_fixtures, show_without_fixtures=False)

@app.cli.command('populate_dummy_data')
def populate_dummy_data():
    # Dummy teams
    team_names = ['Dinamo Zagreb', 'HNK Rijeka', 'NK Rudes', 'NK Lokomotiva Zagreb', 'NK Varazdin', 'NK Osijek', 'Istra 1961', 'Slaven Belupo', 'HNK Gorica', 'Hajduk Split']
    for name in team_names:
        team = Team(name=name)
        db.session.add(team)

    # Dummy fixtures
    fixtures_data = [
        {'event_date': '2024-01-28', 'league_id': 1, 'home_team': 'Hajduk Split', 'away_team': 'HNK Rijeka', 'winner': 'HNK Rijeka'},
        {'event_date': '2024-01-28', 'league_id': 1, 'home_team': 'HNK Gorica', 'away_team': 'NK Lokomotiva Zagreb', 'winner': 'NK Lokomotiva Zagreb'},
        {'event_date': '2024-01-27', 'league_id': 1, 'home_team': 'Istra 1961', 'away_team': 'Dinamo Zagreb', 'winner': 'Dinamo Zagreb'},
        {'event_date': '2024-01-27', 'league_id': 1, 'home_team': 'NK Osijek', 'away_team': 'NK Rudes', 'winner': 'NK Osijek'},
        {'event_date': '2024-01-26', 'league_id': 1, 'home_team': 'NK Varazdin', 'away_team': 'Slaven Belupo', 'winner': 'Slaven Belupo'},
        {'event_date': '2024-12-17', 'league_id': 1, 'home_team': 'Dinamo Zagreb', 'away_team': 'Hajduk Split', 'winner': 'Draw'},
        {'event_date': '2024-12-17', 'league_id': 1, 'home_team': 'NK Osijek', 'away_team': 'Slaven Belupo', 'winner': 'NK Osijek'},
        {'event_date': '2024-12-16', 'league_id': 1, 'home_team': 'HNK Rijeka', 'away_team': 'NK Rudes', 'winner': 'HNK Rijeka'},
        {'event_date': '2024-12-16', 'league_id': 1, 'home_team': 'NK Lokomotiva Zagreb', 'away_team': 'Istra 1961', 'winner': 'NK Lokomotiva Zagreb'},
        {'event_date': '2024-12-15', 'league_id': 1, 'home_team': 'HNK Gorica', 'away_team': 'NK Varazdin', 'winner': 'NK Varazdin'},
        {'event_date': '2024-12-10', 'league_id': 1, 'home_team': 'HNK Rijeka', 'away_team': 'Slaven Belupo', 'winner': 'Slaven Belupo'},
        {'event_date': '2024-12-10', 'league_id': 1, 'home_team': 'NK Varazdin', 'away_team': 'NK Osijek', 'winner': 'Draw'},
        {'event_date': '2024-12-09', 'league_id': 1, 'home_team': 'Dinamo Zagreb', 'away_team': 'NK Rudes', 'winner': 'Dinamo Zagreb'},
        {'event_date': '2024-12-09', 'league_id': 1, 'home_team': 'HNK Gorica', 'away_team': 'Istra 1961', 'winner': 'Draw'},
        {'event_date': '2024-12-08', 'league_id': 1, 'home_team': 'NK Lokomotiva Zagreb', 'away_team': 'Hajduk Split', 'winner': 'Draw'},
        {'event_date': '2024-12-04', 'league_id': 1, 'home_team': 'Slaven Belupo', 'away_team': 'Dinamo Zagreb', 'winner': 'Dinamo Zagreb'},
        {'event_date': '2024-12-03', 'league_id': 1, 'home_team': 'NK Rudes', 'away_team': 'NK Lokomotiva Zagreb', 'winner': 'Draw'},
        {'event_date': '2024-12-02', 'league_id': 1, 'home_team': 'Hajduk Split', 'away_team': 'HNK Gorica', 'winner': 'Hajduk Split'},
        {'event_date': '2024-12-02', 'league_id': 1, 'home_team': 'NK Osijek', 'away_team': 'HNK Rijeka', 'winner': 'Draw'},
        {'event_date': '2024-12-01', 'league_id': 1, 'home_team': 'Istra 1961', 'away_team': 'NK Varazdin', 'winner': 'Istra 1961'},



    ]

    for fixture_data in fixtures_data:
        fixture = Fixture(
            event_date=fixture_data['event_date'],
            league_id=fixture_data['league_id'],
            home_team=fixture_data['home_team'],
            away_team=fixture_data['away_team'],
            winner=fixture_data['winner']
        )
        db.session.add(fixture)

    db.session.commit()
    print('Dummy data populated successfully.')


@app.route('/display_league_table', methods=['POST'])
def display_league_table():
    teams = Team.query.all()
    fixtures = Fixture.query.all()

    # Calculate points for each team based on fixtures
    team_points = {team.name: 0 for team in teams}
    for fixture in fixtures:
        if fixture.winner == 'Draw':
            team_points[fixture.home_team] += 1
            team_points[fixture.away_team] += 1
        else:
            team_points[fixture.winner] += 3

    # Sort teams by points in descending order
    sorted_teams = sorted(teams, key=lambda team: team_points[team.name], reverse=True)

    return render_template('league_table.html', teams=sorted_teams, team_points=team_points)


@app.route('/download_table', methods=['GET'])
def download_table():
    teams = Team.query.all()
    fixtures = Fixture.query.all()
    team_points = {team.name: 0 for team in teams}
    for fixture in fixtures:
        if fixture.winner == 'Draw':
            team_points[fixture.home_team] += 1
            team_points[fixture.away_team] += 1
        else:
            team_points[fixture.winner] += 3

    # Sort teams by points in descending order
    sorted_teams = sorted(teams, key=lambda team: team_points[team.name], reverse=True)

    df = pd.DataFrame([(team.name, team_points[team.name]) for team in sorted_teams], columns=['Team', 'Points'])
    output = BytesIO()
    df.to_csv(output, index = False, encoding='utf-8')
    output.seek(0)

    return send_file(output, as_attachment = True, download_name = 'Table.csv', mimetype='text/csv')


if __name__ == '__main__':
    app.run(debug=True)
