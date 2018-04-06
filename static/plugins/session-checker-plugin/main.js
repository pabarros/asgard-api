/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};

/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {

/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;

/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			exports: {},
/******/ 			id: moduleId,
/******/ 			loaded: false
/******/ 		};

/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);

/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;

/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}


/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;

/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;

/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";

/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(0);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports, __webpack_require__) {

	"use strict";

	var _assign = __webpack_require__(1);

	var _assign2 = _interopRequireDefault(_assign);

	var _SessionCheckerAction = __webpack_require__(38);

	var _SessionCheckerAction2 = _interopRequireDefault(_SessionCheckerAction);

	var _ChangeAccountComponent = __webpack_require__(39);

	var _ChangeAccountComponent2 = _interopRequireDefault(_ChangeAccountComponent);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    PluginMountPoints = _window$marathonPlugi.PluginMountPoints,
	    PipelineNames = _window$marathonPlugi.PipelineNames,
	    PipelineStore = _window$marathonPlugi.PipelineStore;


	var VERSION = "0.3.0";

	PluginHelper.registerMe();
	_SessionCheckerAction2.default.init();

	if (PipelineNames && PipelineStore) {
	  console.log("Registering PRE_AJAX_REQUEST callback");
	  PipelineStore.registerOperator(PipelineNames.PRE_AJAX_REQUEST, function (data) {
	    var currentHeaders = data.headers;

	    var token = localStorage.getItem("auth_token");
	    currentHeaders["Authorization"] = "JWT " + token;
	    return (0, _assign2.default)({}, data, { headers: currentHeaders });
	  });
	} else {
	  console.log("Request Pipelines feature not found...");
	}

	PluginHelper.injectComponent(_ChangeAccountComponent2.default, PluginMountPoints.NAVBAR_TOP_RIGHT);

/***/ }),
/* 1 */
/***/ (function(module, exports, __webpack_require__) {

	module.exports = { "default": __webpack_require__(2), __esModule: true };

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

	__webpack_require__(3);
	module.exports = __webpack_require__(6).Object.assign;


/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

	// 19.1.3.1 Object.assign(target, source)
	var $export = __webpack_require__(4);

	$export($export.S + $export.F, 'Object', { assign: __webpack_require__(19) });


/***/ }),
/* 4 */
/***/ (function(module, exports, __webpack_require__) {

	var global = __webpack_require__(5);
	var core = __webpack_require__(6);
	var ctx = __webpack_require__(7);
	var hide = __webpack_require__(9);
	var PROTOTYPE = 'prototype';

	var $export = function (type, name, source) {
	  var IS_FORCED = type & $export.F;
	  var IS_GLOBAL = type & $export.G;
	  var IS_STATIC = type & $export.S;
	  var IS_PROTO = type & $export.P;
	  var IS_BIND = type & $export.B;
	  var IS_WRAP = type & $export.W;
	  var exports = IS_GLOBAL ? core : core[name] || (core[name] = {});
	  var expProto = exports[PROTOTYPE];
	  var target = IS_GLOBAL ? global : IS_STATIC ? global[name] : (global[name] || {})[PROTOTYPE];
	  var key, own, out;
	  if (IS_GLOBAL) source = name;
	  for (key in source) {
	    // contains in native
	    own = !IS_FORCED && target && target[key] !== undefined;
	    if (own && key in exports) continue;
	    // export native or passed
	    out = own ? target[key] : source[key];
	    // prevent global pollution for namespaces
	    exports[key] = IS_GLOBAL && typeof target[key] != 'function' ? source[key]
	    // bind timers to global for call from export context
	    : IS_BIND && own ? ctx(out, global)
	    // wrap global constructors for prevent change them in library
	    : IS_WRAP && target[key] == out ? (function (C) {
	      var F = function (a, b, c) {
	        if (this instanceof C) {
	          switch (arguments.length) {
	            case 0: return new C();
	            case 1: return new C(a);
	            case 2: return new C(a, b);
	          } return new C(a, b, c);
	        } return C.apply(this, arguments);
	      };
	      F[PROTOTYPE] = C[PROTOTYPE];
	      return F;
	    // make static versions for prototype methods
	    })(out) : IS_PROTO && typeof out == 'function' ? ctx(Function.call, out) : out;
	    // export proto methods to core.%CONSTRUCTOR%.methods.%NAME%
	    if (IS_PROTO) {
	      (exports.virtual || (exports.virtual = {}))[key] = out;
	      // export proto methods to core.%CONSTRUCTOR%.prototype.%NAME%
	      if (type & $export.R && expProto && !expProto[key]) hide(expProto, key, out);
	    }
	  }
	};
	// type bitmap
	$export.F = 1;   // forced
	$export.G = 2;   // global
	$export.S = 4;   // static
	$export.P = 8;   // proto
	$export.B = 16;  // bind
	$export.W = 32;  // wrap
	$export.U = 64;  // safe
	$export.R = 128; // real proto method for `library`
	module.exports = $export;


/***/ }),
/* 5 */
/***/ (function(module, exports) {

	// https://github.com/zloirock/core-js/issues/86#issuecomment-115759028
	var global = module.exports = typeof window != 'undefined' && window.Math == Math
	  ? window : typeof self != 'undefined' && self.Math == Math ? self
	  // eslint-disable-next-line no-new-func
	  : Function('return this')();
	if (typeof __g == 'number') __g = global; // eslint-disable-line no-undef


/***/ }),
/* 6 */
/***/ (function(module, exports) {

	var core = module.exports = { version: '2.5.3' };
	if (typeof __e == 'number') __e = core; // eslint-disable-line no-undef


/***/ }),
/* 7 */
/***/ (function(module, exports, __webpack_require__) {

	// optional / simple context binding
	var aFunction = __webpack_require__(8);
	module.exports = function (fn, that, length) {
	  aFunction(fn);
	  if (that === undefined) return fn;
	  switch (length) {
	    case 1: return function (a) {
	      return fn.call(that, a);
	    };
	    case 2: return function (a, b) {
	      return fn.call(that, a, b);
	    };
	    case 3: return function (a, b, c) {
	      return fn.call(that, a, b, c);
	    };
	  }
	  return function (/* ...args */) {
	    return fn.apply(that, arguments);
	  };
	};


/***/ }),
/* 8 */
/***/ (function(module, exports) {

	module.exports = function (it) {
	  if (typeof it != 'function') throw TypeError(it + ' is not a function!');
	  return it;
	};


/***/ }),
/* 9 */
/***/ (function(module, exports, __webpack_require__) {

	var dP = __webpack_require__(10);
	var createDesc = __webpack_require__(18);
	module.exports = __webpack_require__(14) ? function (object, key, value) {
	  return dP.f(object, key, createDesc(1, value));
	} : function (object, key, value) {
	  object[key] = value;
	  return object;
	};


/***/ }),
/* 10 */
/***/ (function(module, exports, __webpack_require__) {

	var anObject = __webpack_require__(11);
	var IE8_DOM_DEFINE = __webpack_require__(13);
	var toPrimitive = __webpack_require__(17);
	var dP = Object.defineProperty;

	exports.f = __webpack_require__(14) ? Object.defineProperty : function defineProperty(O, P, Attributes) {
	  anObject(O);
	  P = toPrimitive(P, true);
	  anObject(Attributes);
	  if (IE8_DOM_DEFINE) try {
	    return dP(O, P, Attributes);
	  } catch (e) { /* empty */ }
	  if ('get' in Attributes || 'set' in Attributes) throw TypeError('Accessors not supported!');
	  if ('value' in Attributes) O[P] = Attributes.value;
	  return O;
	};


/***/ }),
/* 11 */
/***/ (function(module, exports, __webpack_require__) {

	var isObject = __webpack_require__(12);
	module.exports = function (it) {
	  if (!isObject(it)) throw TypeError(it + ' is not an object!');
	  return it;
	};


/***/ }),
/* 12 */
/***/ (function(module, exports) {

	module.exports = function (it) {
	  return typeof it === 'object' ? it !== null : typeof it === 'function';
	};


/***/ }),
/* 13 */
/***/ (function(module, exports, __webpack_require__) {

	module.exports = !__webpack_require__(14) && !__webpack_require__(15)(function () {
	  return Object.defineProperty(__webpack_require__(16)('div'), 'a', { get: function () { return 7; } }).a != 7;
	});


/***/ }),
/* 14 */
/***/ (function(module, exports, __webpack_require__) {

	// Thank's IE8 for his funny defineProperty
	module.exports = !__webpack_require__(15)(function () {
	  return Object.defineProperty({}, 'a', { get: function () { return 7; } }).a != 7;
	});


/***/ }),
/* 15 */
/***/ (function(module, exports) {

	module.exports = function (exec) {
	  try {
	    return !!exec();
	  } catch (e) {
	    return true;
	  }
	};


/***/ }),
/* 16 */
/***/ (function(module, exports, __webpack_require__) {

	var isObject = __webpack_require__(12);
	var document = __webpack_require__(5).document;
	// typeof document.createElement is 'object' in old IE
	var is = isObject(document) && isObject(document.createElement);
	module.exports = function (it) {
	  return is ? document.createElement(it) : {};
	};


/***/ }),
/* 17 */
/***/ (function(module, exports, __webpack_require__) {

	// 7.1.1 ToPrimitive(input [, PreferredType])
	var isObject = __webpack_require__(12);
	// instead of the ES6 spec version, we didn't implement @@toPrimitive case
	// and the second argument - flag - preferred type is a string
	module.exports = function (it, S) {
	  if (!isObject(it)) return it;
	  var fn, val;
	  if (S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
	  if (typeof (fn = it.valueOf) == 'function' && !isObject(val = fn.call(it))) return val;
	  if (!S && typeof (fn = it.toString) == 'function' && !isObject(val = fn.call(it))) return val;
	  throw TypeError("Can't convert object to primitive value");
	};


/***/ }),
/* 18 */
/***/ (function(module, exports) {

	module.exports = function (bitmap, value) {
	  return {
	    enumerable: !(bitmap & 1),
	    configurable: !(bitmap & 2),
	    writable: !(bitmap & 4),
	    value: value
	  };
	};


/***/ }),
/* 19 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';
	// 19.1.2.1 Object.assign(target, source, ...)
	var getKeys = __webpack_require__(20);
	var gOPS = __webpack_require__(35);
	var pIE = __webpack_require__(36);
	var toObject = __webpack_require__(37);
	var IObject = __webpack_require__(24);
	var $assign = Object.assign;

	// should work with symbols and should have deterministic property order (V8 bug)
	module.exports = !$assign || __webpack_require__(15)(function () {
	  var A = {};
	  var B = {};
	  // eslint-disable-next-line no-undef
	  var S = Symbol();
	  var K = 'abcdefghijklmnopqrst';
	  A[S] = 7;
	  K.split('').forEach(function (k) { B[k] = k; });
	  return $assign({}, A)[S] != 7 || Object.keys($assign({}, B)).join('') != K;
	}) ? function assign(target, source) { // eslint-disable-line no-unused-vars
	  var T = toObject(target);
	  var aLen = arguments.length;
	  var index = 1;
	  var getSymbols = gOPS.f;
	  var isEnum = pIE.f;
	  while (aLen > index) {
	    var S = IObject(arguments[index++]);
	    var keys = getSymbols ? getKeys(S).concat(getSymbols(S)) : getKeys(S);
	    var length = keys.length;
	    var j = 0;
	    var key;
	    while (length > j) if (isEnum.call(S, key = keys[j++])) T[key] = S[key];
	  } return T;
	} : $assign;


/***/ }),
/* 20 */
/***/ (function(module, exports, __webpack_require__) {

	// 19.1.2.14 / 15.2.3.14 Object.keys(O)
	var $keys = __webpack_require__(21);
	var enumBugKeys = __webpack_require__(34);

	module.exports = Object.keys || function keys(O) {
	  return $keys(O, enumBugKeys);
	};


/***/ }),
/* 21 */
/***/ (function(module, exports, __webpack_require__) {

	var has = __webpack_require__(22);
	var toIObject = __webpack_require__(23);
	var arrayIndexOf = __webpack_require__(27)(false);
	var IE_PROTO = __webpack_require__(31)('IE_PROTO');

	module.exports = function (object, names) {
	  var O = toIObject(object);
	  var i = 0;
	  var result = [];
	  var key;
	  for (key in O) if (key != IE_PROTO) has(O, key) && result.push(key);
	  // Don't enum bug & hidden keys
	  while (names.length > i) if (has(O, key = names[i++])) {
	    ~arrayIndexOf(result, key) || result.push(key);
	  }
	  return result;
	};


/***/ }),
/* 22 */
/***/ (function(module, exports) {

	var hasOwnProperty = {}.hasOwnProperty;
	module.exports = function (it, key) {
	  return hasOwnProperty.call(it, key);
	};


/***/ }),
/* 23 */
/***/ (function(module, exports, __webpack_require__) {

	// to indexed object, toObject with fallback for non-array-like ES3 strings
	var IObject = __webpack_require__(24);
	var defined = __webpack_require__(26);
	module.exports = function (it) {
	  return IObject(defined(it));
	};


/***/ }),
/* 24 */
/***/ (function(module, exports, __webpack_require__) {

	// fallback for non-array-like ES3 and non-enumerable old V8 strings
	var cof = __webpack_require__(25);
	// eslint-disable-next-line no-prototype-builtins
	module.exports = Object('z').propertyIsEnumerable(0) ? Object : function (it) {
	  return cof(it) == 'String' ? it.split('') : Object(it);
	};


/***/ }),
/* 25 */
/***/ (function(module, exports) {

	var toString = {}.toString;

	module.exports = function (it) {
	  return toString.call(it).slice(8, -1);
	};


/***/ }),
/* 26 */
/***/ (function(module, exports) {

	// 7.2.1 RequireObjectCoercible(argument)
	module.exports = function (it) {
	  if (it == undefined) throw TypeError("Can't call method on  " + it);
	  return it;
	};


/***/ }),
/* 27 */
/***/ (function(module, exports, __webpack_require__) {

	// false -> Array#indexOf
	// true  -> Array#includes
	var toIObject = __webpack_require__(23);
	var toLength = __webpack_require__(28);
	var toAbsoluteIndex = __webpack_require__(30);
	module.exports = function (IS_INCLUDES) {
	  return function ($this, el, fromIndex) {
	    var O = toIObject($this);
	    var length = toLength(O.length);
	    var index = toAbsoluteIndex(fromIndex, length);
	    var value;
	    // Array#includes uses SameValueZero equality algorithm
	    // eslint-disable-next-line no-self-compare
	    if (IS_INCLUDES && el != el) while (length > index) {
	      value = O[index++];
	      // eslint-disable-next-line no-self-compare
	      if (value != value) return true;
	    // Array#indexOf ignores holes, Array#includes - not
	    } else for (;length > index; index++) if (IS_INCLUDES || index in O) {
	      if (O[index] === el) return IS_INCLUDES || index || 0;
	    } return !IS_INCLUDES && -1;
	  };
	};


/***/ }),
/* 28 */
/***/ (function(module, exports, __webpack_require__) {

	// 7.1.15 ToLength
	var toInteger = __webpack_require__(29);
	var min = Math.min;
	module.exports = function (it) {
	  return it > 0 ? min(toInteger(it), 0x1fffffffffffff) : 0; // pow(2, 53) - 1 == 9007199254740991
	};


/***/ }),
/* 29 */
/***/ (function(module, exports) {

	// 7.1.4 ToInteger
	var ceil = Math.ceil;
	var floor = Math.floor;
	module.exports = function (it) {
	  return isNaN(it = +it) ? 0 : (it > 0 ? floor : ceil)(it);
	};


/***/ }),
/* 30 */
/***/ (function(module, exports, __webpack_require__) {

	var toInteger = __webpack_require__(29);
	var max = Math.max;
	var min = Math.min;
	module.exports = function (index, length) {
	  index = toInteger(index);
	  return index < 0 ? max(index + length, 0) : min(index, length);
	};


/***/ }),
/* 31 */
/***/ (function(module, exports, __webpack_require__) {

	var shared = __webpack_require__(32)('keys');
	var uid = __webpack_require__(33);
	module.exports = function (key) {
	  return shared[key] || (shared[key] = uid(key));
	};


/***/ }),
/* 32 */
/***/ (function(module, exports, __webpack_require__) {

	var global = __webpack_require__(5);
	var SHARED = '__core-js_shared__';
	var store = global[SHARED] || (global[SHARED] = {});
	module.exports = function (key) {
	  return store[key] || (store[key] = {});
	};


/***/ }),
/* 33 */
/***/ (function(module, exports) {

	var id = 0;
	var px = Math.random();
	module.exports = function (key) {
	  return 'Symbol('.concat(key === undefined ? '' : key, ')_', (++id + px).toString(36));
	};


/***/ }),
/* 34 */
/***/ (function(module, exports) {

	// IE 8- don't enum bug keys
	module.exports = (
	  'constructor,hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf'
	).split(',');


/***/ }),
/* 35 */
/***/ (function(module, exports) {

	exports.f = Object.getOwnPropertySymbols;


/***/ }),
/* 36 */
/***/ (function(module, exports) {

	exports.f = {}.propertyIsEnumerable;


/***/ }),
/* 37 */
/***/ (function(module, exports, __webpack_require__) {

	// 7.1.13 ToObject(argument)
	var defined = __webpack_require__(26);
	module.exports = function (it) {
	  return Object(defined(it));
	};


/***/ }),
/* 38 */
/***/ (function(module, exports) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});
	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginActions = _window$marathonPlugi.PluginActions,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    Bridge = _window$marathonPlugi.Bridge,
	    MarathonService = _window$marathonPlugi.MarathonService;


	var acceptDialog = function acceptDialog(dialog) {
	  if (dialog.myid === "session-expired") {
	    Bridge.navigateTo("/login");
	  }
	};

	function checkStatusCode(statusCode) {
	  if (statusCode === 401) {
	    PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	      title: "Sua sessão expirou",
	      message: "Por favor faça login novamente",
	      actionButtonLabel: "Login",
	      myid: "session-expired"
	    }]);
	  }
	}

	Bridge.DialogStore.on("DIALOG_EVENTS_ACCEPT_DIALOG", acceptDialog);

	function checkSession() {
	  MarathonService.request({
	    resource: "v2/deployments",
	    concurrent: true
	  }).success(function (response) {}).error(function (error) {
	    checkStatusCode(error.status);
	  });
	}

	var SessionCheckerAction = {
	  init: function init() {
	    setInterval(checkSession, 5000);
	  }
	};

	exports.default = SessionCheckerAction;

/***/ }),
/* 39 */
/***/ (function(module, exports, __webpack_require__) {

	"use strict";

	Object.defineProperty(exports, "__esModule", {
	  value: true
	});

	var _addons = __webpack_require__(40);

	var _addons2 = _interopRequireDefault(_addons);

	var _jwtDecode = __webpack_require__(41);

	var _jwtDecode2 = _interopRequireDefault(_jwtDecode);

	function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

	/* eslint-enable camelcase */

	var _window$marathonPlugi = window.marathonPluginInterface,
	    PluginActions = _window$marathonPlugi.PluginActions,
	    PluginHelper = _window$marathonPlugi.PluginHelper,
	    Bridge = _window$marathonPlugi.Bridge,
	    MarathonService = _window$marathonPlugi.MarathonService;
	/* eslint-disable camelcase */

	function showErrorDialog(title, message) {

	  PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	    title: title,
	    message: message,
	    actionButtonLabel: "OK"
	  }]);
	}

	var ChangeAccountComponent = _addons2.default.createClass({
	  displayName: "ChangeAccountComponent",

	  handleMenuClick: function handleMenuClick() {
	    PluginHelper.callAction(PluginActions.DIALOG_ALERT, [{
	      title: "Trocar de conta",
	      message: "Por favor escolha a conta",
	      actionButtonLabel: "OK",
	      myid: "session-account-change"
	    }]);
	  },

	  getInitialState: function getInitialState() {
	    return {
	      User: {},
	      CurrentAccount: {}
	    };
	  },

	  acceptChangeAccountDialog: function acceptChangeAccountDialog(dialog) {
	    var _this = this;

	    if (dialog.myid === "session-account-change") {
	      MarathonService.request({
	        resource: "hollow/account/next",
	        method: "POST"
	      }).error(function (error) {
	        showErrorDialog("Erro ao trocar de conta", error.body.msg);
	      }).success(function (response) {
	        _this.setState({
	          User: response.body.user,
	          CurrentAccount: response.body.current_account
	        });
	        localStorage.setItem("auth_token", response.body.jwt_token);
	      });
	      Bridge.navigateTo("/#/apps");
	    }
	  },

	  componentDidMount: function componentDidMount() {
	    this.startPolling();
	  },

	  whoAmI: function whoAmI() {
	    var _this2 = this;

	    /* eslint-disable no-unused-vars */
	    MarathonService.request({ resource: "hollow/account/me", method: "GET" }).error(function (error) {
	      /* Não temos muito o que fazer aqui. Se retornar erro,
	       * já estamos deslogados e isso já é tratado por outra
	       * parte desse plugin. E se estamos deslogados,
	       * não temos o que exiibir nesse componente.
	        */
	    }).success(function (response) {
	      _this2.setState({
	        User: response.body.user,
	        CurrentAccount: response.body.current_account
	      });
	    });
	    /* eslint-enable no-unused-vars */
	  },

	  componentWillMount: function componentWillMount() {
	    Bridge.DialogStore.on("DIALOG_EVENTS_ACCEPT_DIALOG", this.acceptChangeAccountDialog);
	    this.whoAmI();
	  },

	  render: function render() {
	    return _addons2.default.createElement(
	      "div",
	      { className: "help-menu active",
	        onClick: this.handleMenuClick },
	      _addons2.default.createElement(
	        "span",
	        null,
	        " ",
	        this.state.User.name,
	        "@",
	        this.state.CurrentAccount.name,
	        " "
	      )
	    );
	  },

	  reReadToken: function reReadToken() {
	    /* eslint-disable no-empty */
	    try {
	      var token = (0, _jwtDecode2.default)(localStorage.getItem("auth_token"));
	      this.setState({
	        User: token.user,
	        CurrentAccount: token.current_account
	      });
	    } catch (e) {}
	    /* eslint-enable no-empty */
	  },

	  startPolling: function startPolling() {
	    if (this.interval == null) {
	      this.interval = setInterval(this.reReadToken, 5000);
	    }
	  }
	});

	exports.default = ChangeAccountComponent;

/***/ }),
/* 40 */
/***/ (function(module, exports) {

	"use strict";

	// This is a direct replacement for React and used to automatically substitute
	// React with the injected instance.
	// This is necessary, as using a different React instance will result in
	// various "Invariant Violation" errors.
	// It's getting the injected instance from the marathon plugin interface and
	// provide it to the plugin using the CommonJS syntax export for greater
	// compatibility with old modules.
	var React = window.marathonPluginInterface.React;

	module.exports = React;

/***/ }),
/* 41 */
/***/ (function(module, exports, __webpack_require__) {

	'use strict';

	var base64_url_decode = __webpack_require__(42);

	function InvalidTokenError(message) {
	  this.message = message;
	}

	InvalidTokenError.prototype = new Error();
	InvalidTokenError.prototype.name = 'InvalidTokenError';

	module.exports = function (token,options) {
	  if (typeof token !== 'string') {
	    throw new InvalidTokenError('Invalid token specified');
	  }

	  options = options || {};
	  var pos = options.header === true ? 0 : 1;
	  try {
	    return JSON.parse(base64_url_decode(token.split('.')[pos]));
	  } catch (e) {
	    throw new InvalidTokenError('Invalid token specified: ' + e.message);
	  }
	};

	module.exports.InvalidTokenError = InvalidTokenError;


/***/ }),
/* 42 */
/***/ (function(module, exports, __webpack_require__) {

	var atob = __webpack_require__(43);

	function b64DecodeUnicode(str) {
	  return decodeURIComponent(atob(str).replace(/(.)/g, function (m, p) {
	    var code = p.charCodeAt(0).toString(16).toUpperCase();
	    if (code.length < 2) {
	      code = '0' + code;
	    }
	    return '%' + code;
	  }));
	}

	module.exports = function(str) {
	  var output = str.replace(/-/g, "+").replace(/_/g, "/");
	  switch (output.length % 4) {
	    case 0:
	      break;
	    case 2:
	      output += "==";
	      break;
	    case 3:
	      output += "=";
	      break;
	    default:
	      throw "Illegal base64url string!";
	  }

	  try{
	    return b64DecodeUnicode(output);
	  } catch (err) {
	    return atob(output);
	  }
	};


/***/ }),
/* 43 */
/***/ (function(module, exports) {

	/**
	 * The code was extracted from:
	 * https://github.com/davidchambers/Base64.js
	 */

	var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

	function InvalidCharacterError(message) {
	  this.message = message;
	}

	InvalidCharacterError.prototype = new Error();
	InvalidCharacterError.prototype.name = 'InvalidCharacterError';

	function polyfill (input) {
	  var str = String(input).replace(/=+$/, '');
	  if (str.length % 4 == 1) {
	    throw new InvalidCharacterError("'atob' failed: The string to be decoded is not correctly encoded.");
	  }
	  for (
	    // initialize result and counters
	    var bc = 0, bs, buffer, idx = 0, output = '';
	    // get next character
	    buffer = str.charAt(idx++);
	    // character found in table? initialize bit storage and add its ascii value;
	    ~buffer && (bs = bc % 4 ? bs * 64 + buffer : buffer,
	      // and if not first of each 4 characters,
	      // convert the first 8 bits to one ascii character
	      bc++ % 4) ? output += String.fromCharCode(255 & bs >> (-2 * bc & 6)) : 0
	  ) {
	    // try to find character in table (0-63, not found => -1)
	    buffer = chars.indexOf(buffer);
	  }
	  return output;
	}


	module.exports = typeof window !== 'undefined' && window.atob && window.atob.bind(window) || polyfill;


/***/ })
/******/ ]);