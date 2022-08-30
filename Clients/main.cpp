#include <iostream>
#include <string>
#include <vector>

using namespace std;

enum Action
{
    STAY,
    MOVE_DOWN,
    MOVE_UP,
    MOVE_RIGHT,
    MOVE_LEFT,
    UPGRADE_DEFENCE,
    UPGRADE_ATTACK,
    LINEAR_ATTACK_DOWN,
    LINEAR_ATTACK_UP,
    LINEAR_ATTACK_RIGHT,
    LINEAR_ATTACK_LEFT,
    RANGED_ATTACK
};

enum MapType
{
    EMPTY,
    AGENT,
    GOLD,
    TREASURY,
    WALL,
    FOG,
    OUT_OF_SIGHT,
    OUT_OF_MAP
};

istream& operator>>(istream& is, MapType& type)
{
    int tmp;
    if (is >> tmp) {
        type = static_cast<MapType>(tmp);
    }
    return is;
}

class MapTile
{
public:
    MapType type;
    int data;
    pair<int, int> coordinates;
};

class Map
{
public:
    int width, height;
    int goldCount;
    int sightRange;
    vector<MapTile> grid;

    void setGridSize() {
        grid = vector<MapTile>(sightRange * sightRange);
    }
};

class GameState
{
public:
    GameState() {
        cin >> rounds
            >> defUpgradeCost >> atkUpgradeCost
            >> coolDownRate
            >> linearAttackRange >> rangedAttackRadius
            >> map.width >> map.height
            >> map.goldCount >> map.sightRange;
        map.setGridSize();
    }
    void setInfo() {
        cin >> location.first >> location.second;
        for (auto& tile : map.grid) {
            cin >> tile.type >> tile.data
                >> tile.coordinates.first
                >> tile.coordinates.second;
        }
        cin >> agentID >> currentRound >> attackRatio
            >> deflvl >> atklvl
            >> wallet >> safeWallet;
        wallets = vector<int>(4);
        for (auto& w : wallets) {
            cin >> w;
        }
    }
    Action getAction();
    int rounds;
    int defUpgradeCost, atkUpgradeCost;
    float coolDownRate;
    int linearAttackRange, rangedAttackRadius;
    Map map;
    pair<int, int> location;
    int agentID;
    int currentRound;
    float attackRatio;
    int deflvl, atklvl;
    int wallet, safeWallet;
    vector<int> wallets;
};

int main()
{
    GameState game_state;
    for (int i = 0; i < game_state.rounds; i++) {
        game_state.setInfo();
        cout << game_state.getAction() << endl;
    }
    return 0;
}

Action GameState::getAction()
{
    // write your code here
    // return the action value
    return Action::STAY;
}