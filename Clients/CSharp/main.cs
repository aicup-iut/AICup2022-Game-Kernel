using System;
using System.Collections.Generic;

namespace AICUP
{
    public class Point
    {
        public Point() { }
        public int x { get; set; }
        public int y { get; set; }
    };

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

    class MapTile
    {
        public MapType type;
        public int data;
        public Point coordinates = new Point();
    };

    class Map
    {
        public int width, height;
        public int goldCount;
        public int sightRange;
        public MapTile[] grid;

        public void setGridSize()
        {
            grid = new MapTile[sightRange * sightRange];
            for (int i = 0; i < sightRange*sightRange; i++)
            {
                grid[i] = new MapTile();
            }
        }
    };

    class GameState
    {
        public GameState()
        {
            rounds = Convert.ToInt32(Console.ReadLine());
            defUpgradeCost = Convert.ToInt32(Console.ReadLine());
            atkUpgradeCost = Convert.ToInt32(Console.ReadLine());
            coolDownRate = float.Parse(Console.ReadLine());
            linearAttackRange = Convert.ToInt32(Console.ReadLine());
            rangedAttackRadius = Convert.ToInt32(Console.ReadLine());
            var maptok = Console.ReadLine().Split();
            map.width = int.Parse(maptok[0]);
            map.height = int.Parse(maptok[1]);
            map.goldCount = Convert.ToInt32(Console.ReadLine());
            map.sightRange = Convert.ToInt32(Console.ReadLine()); // equivalent to (2r+1)
            map.setGridSize();
        }

        public void setInfo()
        {
            var loctok = Console.ReadLine().Split(); // (row, column)
            location.x = int.Parse(loctok[0]);
            location.y = int.Parse(loctok[1]);
            foreach (var item in map.grid)
            {
                var token = Console.ReadLine().Split();
                item.type = (MapType)int.Parse(token[0]);
                item.data = int.Parse(token[1]);
                item.coordinates.x = int.Parse(token[2]);
                item.coordinates.y = int.Parse(token[3]);
            }
            agentID = Convert.ToInt32(Console.ReadLine()); // player1: 0,1 --- player2: 2,3
            currentRound = Convert.ToInt32(Console.ReadLine()); // 1 indexed
            attackRatio = float.Parse(Console.ReadLine());
            deflvl = Convert.ToInt32(Console.ReadLine());
            atklvl = Convert.ToInt32(Console.ReadLine());
            wallet = Convert.ToInt32(Console.ReadLine());
            safeWallet = Convert.ToInt32(Console.ReadLine());
            wallets = new List<int>(); // current wallet
            var walletstok = Console.ReadLine().Split();
            for (int i = 0; i < 4; i++)
            {
                wallets.Add(int.Parse(walletstok[i]));
            }
            lastAction = Convert.ToInt32(Console.ReadLine()); // -1 if unsuccessful
        }

        public Action getAction()
        {
            // write your code here
            // return the action value
            return Action.STAY;
        }

        public int rounds;
        public int defUpgradeCost, atkUpgradeCost;
        public float coolDownRate;
        public int linearAttackRange, rangedAttackRadius;
        public Map map = new Map();
        public Point location = new Point();
        public int agentID;
        public int currentRound;
        public float attackRatio;
        public int deflvl, atklvl;
        public int wallet, safeWallet;
        List<int> wallets;
        public int lastAction;
    };

    class Program
    {
        static void Main(string[] args)
        {
            GameState game_state = new GameState();
            for (int i = 0; i < game_state.rounds; i++)
            {
                game_state.setInfo();
                Console.WriteLine(Convert.ToInt32(game_state.getAction()));
            }
        }
    }
}