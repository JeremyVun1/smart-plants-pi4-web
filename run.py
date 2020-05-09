from smartplant import create_app, setup_database, LightingModel, SmartPlantDevice, PlantModel, PumpModel, MoistureModel
import argparse

def run_app():
    app = create_app()
    print("APP CREATED")
    setup_database(app)
    app.run(debug=True, host='0.0.0.0', use_reloader=False)


def test_db():
    app = create_app()
    setup_database(app)

    with app.app_context():
        print(SmartPlantDevice.query.all())
        print(PlantModel.query.all())
        print(LightingModel.query.all())
        print(PumpModel.query.all())
        print(MoistureModel.query.all())


def parse_args():
    parser = argparse.ArgumentParser(description='SmartPlant CLI')
    parser.add_argument('-db', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if not args.db:
        run_app()
    elif args.db:
        test_db()

    